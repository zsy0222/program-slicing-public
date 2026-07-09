"""
Java source code parser using javalang.

Extracts statements from a Java method, identifies variable
definitions and uses, and builds the statement list needed
for PDG construction.
"""

from typing import Dict, List, Set, Tuple
import javalang
from javalang.tree import (
    Node, MethodDeclaration, StatementExpression,
    IfStatement, WhileStatement, ForStatement, DoStatement,
    ReturnStatement, VariableDeclaration, LocalVariableDeclaration,
    ThrowStatement, TryStatement, SwitchStatement, AssertStatement,
    BlockStatement, FormalParameter, Assignment,
    MethodInvocation, MemberReference
)

from .models import PDGNode, NodeType


def _get_source_lines(source: str) -> List[str]:
    """Split source into lines."""
    return source.split('\n')


def _find_line(node, source_lines: List[str]) -> int:
    """Find the approximate line number of a javalang AST node."""
    if node is None:
        return 0
    if hasattr(node, 'position') and node.position:
        return node.position.line
    if hasattr(node, '_position') and node._position:
        return node._position.line
    return 0


def _extract_node_code(source_lines: List[str], start_line: int, end_line: int = 0) -> str:
    """Extract source code text for a given line range."""
    if start_line <= 0 or start_line > len(source_lines):
        return ""
    if end_line <= start_line:
        end_line = start_line
    return '\n'.join(source_lines[start_line - 1:end_line]).strip()


class JavaMethodAnalyzer:
    """
    Analyze a single Java method to extract statements, definitions, and uses.
    """

    def __init__(self, source_code: str, method_node: MethodDeclaration):
        self.source_lines = _get_source_lines(source_code)
        self.method_node = method_node
        self.method_name = method_node.name

        # Collected data
        self.statements: List[Tuple[int, str, NodeType, Set[str], Set[str]]] = []
        # Each entry: (line, code, node_type, defined_vars, used_vars)

        # Variables defined by formal parameters
        for param in method_node.parameters or []:
            self.param_vars = {p.name for p in method_node.parameters}
        else:
            self.param_vars = set()

    def analyze(self) -> List[Tuple[int, str, NodeType, Set[str], Set[str]]]:
        """Analyze the method body and return statement list."""
        body = self.method_node.body
        if body is None:
            return self.statements

        if isinstance(body, list):
            for stmt in body:
                self._process_statement(stmt)
        else:
            self._process_statement(body)

        return self.statements

    def analyze_with_branches(self):
        """
        Analyze with branch structure tracking.

        Returns list of (line, code, node_type, defined_vars, used_vars, skip_next,
        is_else_target) where:
        - skip_next: True if after this statement, skip the next N (else body)
        - is_else_target: This statement is the target of a false branch
        """
        body = self.method_node.body
        if body is None:
            return []

        statements = []
        if isinstance(body, list):
            for stmt in body:
                self._process_statement_with_branches(stmt, statements)
        else:
            self._process_statement_with_branches(body, statements)

        return statements

    def _process_statement_with_branches(self, stmt, statements: list, depth=0):
        """Process statement and track branch structure."""
        if stmt is None:
            return

        line = _find_line(stmt, self.source_lines)

        if isinstance(stmt, StatementExpression):
            self._add_branch_stmt(stmt, statements, line)
        elif isinstance(stmt, (LocalVariableDeclaration, VariableDeclaration)):
            self._add_branch_stmt(stmt, statements, line)
        elif isinstance(stmt, IfStatement):
            self._process_if_with_branches(stmt, line, statements, depth)
        elif isinstance(stmt, WhileStatement):
            self._process_while_with_branches(stmt, line, statements, depth)
        elif isinstance(stmt, ForStatement):
            self._process_for_with_branches(stmt, line, statements, depth)
        elif isinstance(stmt, DoStatement):
            self._process_do_branches(stmt, line, statements, depth)
        elif isinstance(stmt, ReturnStatement):
            code = _extract_node_code(self.source_lines, line)
            used = self._extract_identifiers(stmt.expression) if stmt.expression else set()
            statements.append((line, code, NodeType.RETURN, set(), used, 0, 0))
        elif isinstance(stmt, ThrowStatement):
            code = _extract_node_code(self.source_lines, line)
            used = self._extract_identifiers(stmt.expression)
            statements.append((line, code, NodeType.RETURN, set(), used, 0, 0))
        elif isinstance(stmt, AssertStatement):
            code = _extract_node_code(self.source_lines, line)
            used = self._extract_identifiers(stmt.condition)
            statements.append((line, code, NodeType.OTHER, set(), used, 0, 0))
        elif isinstance(stmt, TryStatement):
            self._process_try_branches(stmt, line, statements, depth)
        elif isinstance(stmt, SwitchStatement):
            self._process_switch_branches(stmt, line, statements, depth)
        elif isinstance(stmt, BlockStatement):
            for s in stmt.statements or []:
                self._process_statement_with_branches(s, statements, depth)
        else:
            # Catch-all for unhandled statement types
            code = _extract_node_code(self.source_lines, line)
            used = self._extract_identifiers(stmt)
            statements.append((line, code if code else str(stmt)[:80],
                             NodeType.OTHER, set(), used, 0, 0))

    def _add_branch_stmt(self, stmt, statements: list, line):
        """Add a simple statement with branch tracking (7-tuple)."""
        code = _extract_node_code(self.source_lines, line)
        defined = set()
        used = set()
        node_type = NodeType.OTHER

        if isinstance(stmt, StatementExpression):
            expr = stmt.expression
            if isinstance(expr, Assignment):
                defined = self._extract_variables_from_lhs(expr.expressionl)
                used = self._extract_identifiers(expr.value)
                node_type = NodeType.ASSIGNMENT
            elif isinstance(expr, MethodInvocation):
                used = self._extract_identifiers(expr)
                node_type = NodeType.METHOD_CALL
            else:
                used = self._extract_identifiers(expr)
        elif isinstance(stmt, LocalVariableDeclaration):
            for decl in stmt.declarators or []:
                defined.add(decl.name)
                if decl.initializer:
                    used.update(self._extract_identifiers(decl.initializer))
            node_type = NodeType.DECLARATION
        elif isinstance(stmt, VariableDeclaration):
            for decl in stmt.declarators or []:
                defined.add(decl.name)
                if decl.initializer:
                    used.update(self._extract_identifiers(decl.initializer))
            node_type = NodeType.DECLARATION

        # Always 7-tuple: (line, code, node_type, defined, used, extra_flags, skip_next)
        statements.append((line, code, node_type, defined, used, 0, 0))

    def _process_if_with_branches(self, stmt: IfStatement, line, statements, depth):
        """Process if(-else) with accurate branch tracking."""
        cond_code = "if (" + _extract_node_code(self.source_lines, line).split('(')[-1].rstrip(')') + ")"
        cond_used = self._extract_identifiers(stmt.condition)
        statements.append((line, cond_code, NodeType.CONDITION, set(), cond_used))

        # Process then body
        then_start = len(statements)
        if isinstance(stmt.then_statement, BlockStatement):
            for s in stmt.then_statement.statements or []:
                self._process_statement_with_branches(s, statements, depth + 1)
        else:
            self._process_statement_with_branches(stmt.then_statement, statements, depth + 1)

        then_end = len(statements)

        # Process else body (if present)
        has_else = stmt.else_statement is not None
        if has_else:
            # Mark the first else statement as a branch target
            else_start = len(statements)
            if isinstance(stmt.else_statement, BlockStatement):
                for s in stmt.else_statement.statements or []:
                    self._process_statement_with_branches(s, statements, depth + 1)
            else:
                self._process_statement_with_branches(stmt.else_statement, statements, depth + 1)
            else_end = len(statements)

            # After then body, skip the else block
            if then_end > then_start:
                before = statements[then_end - 1]
                # Replace skip_next at index 6
                statements[then_end - 1] = before[:6] + (else_end - then_end,)
        else:
            else_end = then_end
            if then_end > then_start:
                before = statements[then_end - 1]
                statements[then_end - 1] = before[:6] + (0,)

    def _process_while_with_branches(self, stmt: WhileStatement, line, statements, depth):
        """Process while loop."""
        cond_code = "while (" + _extract_node_code(self.source_lines, line).split('(')[-1].rstrip(')') + ")"
        cond_used = self._extract_identifiers(stmt.condition)
        statements.append((line, cond_code, NodeType.CONDITION, set(), cond_used))

        if isinstance(stmt.body, BlockStatement):
            for s in stmt.body.statements or []:
                self._process_statement_with_branches(s, statements, depth + 1)
        else:
            self._process_statement_with_branches(stmt.body, statements, depth + 1)

    def _process_for_with_branches(self, stmt, line, statements, depth):
        """Process for loop."""
        cond_used = set()
        if stmt.control and stmt.control.condition:
            cond_used = self._extract_identifiers(stmt.control.condition)
        cond_code = "for(...;" + (_extract_node_code(self.source_lines, line).split(';')[-1].strip().rstrip(')') if ';' in _extract_node_code(self.source_lines, line) else "...") + ")"
        statements.append((line, cond_code, NodeType.CONDITION, set(), cond_used))

        if isinstance(stmt.body, BlockStatement):
            for s in stmt.body.statements or []:
                self._process_statement_with_branches(s, statements, depth + 1)
        else:
            self._process_statement_with_branches(stmt.body, statements, depth + 1)

    def _process_do_branches(self, stmt, line, statements, depth):
        """Process do-while."""
        cond_used = self._extract_identifiers(stmt.condition)
        statements.append(("do", f"while ({_extract_node_code(self.source_lines, line)})", NodeType.CONDITION, set(), cond_used))
        if isinstance(stmt.body, BlockStatement):
            for s in stmt.body.statements or []:
                self._process_statement_with_branches(s, statements, depth + 1)

    def _process_switch_branches(self, stmt, line, statements, depth):
        self._process_switch(stmt, line)

    def _process_try_branches(self, stmt, line, statements, depth):
        self._process_try(stmt, line)

    def _add_statement(self, line: int, code: str, node_type: NodeType,
                       defined: Set[str], used: Set[str], end_line: int = 0):
        """Add a statement to the list."""
        if code.strip():
            self.statements.append((line, code, node_type, defined, used))

    def _extract_identifiers(self, node) -> Set[str]:
        """Recursively extract all variable identifiers from an AST node."""
        ids = set()
        if node is None:
            return ids

        # Handle leaf identifier nodes
        if isinstance(node, javalang.tree.MemberReference):
            ids.add(node.member)
            if node.prefix_operators:
                for op in node.prefix_operators:
                    ids.update(self._extract_identifiers(op))
            if node.selectors:
                for sel in node.selectors:
                    ids.update(self._extract_identifiers(sel))
            return ids

        if isinstance(node, javalang.tree.Literal):
            return ids  # skip numeric/string literals
        if isinstance(node, javalang.tree.BasicType):
            return ids  # skip type references

        # Handle nodes with a 'name' attribute (variable references)
        if hasattr(node, 'name') and isinstance(node.name, str):
            ids.add(node.name)

        # Generic recursive traversal via children list
        children = []
        try:
            children = node.children or []
        except Exception:
            return ids

        for child in children:
            if child is None:
                continue
            if isinstance(child, (list, tuple, set)):
                for item in child:
                    ids.update(self._extract_identifiers(item))
            elif isinstance(child, (str, int, float, bool)):
                continue
            else:
                ids.update(self._extract_identifiers(child))

        return ids

    def _process_statement(self, stmt, end_line: int = 0):
        """Process a single statement and dispatch to type-specific handlers."""
        if stmt is None:
            return

        line = _find_line(stmt, self.source_lines)

        if isinstance(stmt, StatementExpression):
            self._process_expression_stmt(stmt, line)
        elif isinstance(stmt, LocalVariableDeclaration):
            self._process_var_decl(stmt, line)
        elif isinstance(stmt, IfStatement):
            self._process_if(stmt, line)
        elif isinstance(stmt, WhileStatement):
            self._process_while(stmt, line)
        elif isinstance(stmt, ForStatement):
            self._process_for(stmt, line)
        elif isinstance(stmt, DoStatement):
            self._process_do_while(stmt, line)
        elif isinstance(stmt, ReturnStatement):
            self._process_return(stmt, line)
        elif isinstance(stmt, ThrowStatement):
            self._process_throw(stmt, line)
        elif isinstance(stmt, TryStatement):
            self._process_try(stmt, line)
        elif isinstance(stmt, SwitchStatement):
            self._process_switch(stmt, line)
        elif isinstance(stmt, BlockStatement):
            for s in stmt.statements or []:
                self._process_statement(s)
        elif isinstance(stmt, VariableDeclaration):
            self._process_var_decl(stmt, line)
        else:
            # Catch-all: treat as other
            code = _extract_node_code(self.source_lines, line)
            used = self._extract_identifiers(stmt)
            self._add_statement(line, code, NodeType.OTHER, set(), used)

    def _process_expression_stmt(self, stmt: StatementExpression, line: int):
        """Process expression statement (assignment or method call)."""
        expr = stmt.expression
        code = _extract_node_code(self.source_lines, line)
        defined = set()
        used = set()

        if isinstance(expr, Assignment):
            # LHS = RHS
            target_ids = self._extract_variables_from_lhs(expr.expressionl)
            defined.update(target_ids)
            used.update(self._extract_identifiers(expr.value))
            node_type = NodeType.ASSIGNMENT
        elif isinstance(expr, MethodInvocation):
            used.update(self._extract_identifiers(expr))
            node_type = NodeType.METHOD_CALL
            # If there's a qualifier like obj.method(), obj is used
            if hasattr(expr, 'qualifier') and expr.qualifier:
                if isinstance(expr.qualifier, str):
                    used.add(expr.qualifier)
        else:
            used.update(self._extract_identifiers(expr))
            node_type = NodeType.OTHER

        self._add_statement(line, code, node_type, defined, used)

    def _extract_variables_from_lhs(self, node) -> Set[str]:
        """Extract variable names from the left-hand side of an assignment."""
        if node is None:
            return set()
        if isinstance(node, javalang.tree.MemberReference):
            return {node.member}
        if hasattr(node, 'name') and isinstance(node.name, str):
            return {node.name}
        # For array access etc., traverse children
        ids = set()
        try:
            for child in (node.children or []):
                if child is None:
                    continue
                if isinstance(child, (list, tuple)):
                    for item in child:
                        ids.update(self._extract_variables_from_lhs(item))
                elif not isinstance(child, (str, int, float, bool)):
                    ids.update(self._extract_variables_from_lhs(child))
        except Exception:
            pass
        return ids

    def _process_var_decl(self, stmt, line: int):
        """Process local variable declaration."""
        code = _extract_node_code(self.source_lines, line)
        defined = set()
        used = set()

        if isinstance(stmt, LocalVariableDeclaration):
            for decl in stmt.declarators or []:
                defined.add(decl.name)
                if hasattr(decl, 'initializer') and decl.initializer:
                    used.update(self._extract_identifiers(decl.initializer))
        elif isinstance(stmt, VariableDeclaration):
            for decl in stmt.declarators or []:
                defined.add(decl.name)
                if hasattr(decl, 'initializer') and decl.initializer:
                    used.update(self._extract_identifiers(decl.initializer))

        self._add_statement(line, code, NodeType.DECLARATION, defined, used)

    def _process_if(self, stmt: IfStatement, line: int):
        """Process if statement."""
        # The condition is a separate node (control dependency source)
        cond_code = "if (" + _extract_node_code(self.source_lines, line).split('(')[-1].rstrip(')') + ")"
        cond_used = self._extract_identifiers(stmt.condition)
        self._add_statement(line, cond_code, NodeType.CONDITION, set(), cond_used)

        # Process then block
        if isinstance(stmt.then_statement, BlockStatement):
            for s in stmt.then_statement.statements or []:
                self._process_statement(s)
        else:
            self._process_statement(stmt.then_statement)

        # Process else block
        if stmt.else_statement:
            if isinstance(stmt.else_statement, BlockStatement):
                for s in stmt.else_statement.statements or []:
                    self._process_statement(s)
            else:
                self._process_statement(stmt.else_statement)

    def _process_while(self, stmt: WhileStatement, line: int):
        """Process while loop."""
        cond_code = "while (" + _extract_node_code(self.source_lines, line).split('(')[-1].rstrip(')') + ")"
        cond_used = self._extract_identifiers(stmt.condition)
        self._add_statement(line, cond_code, NodeType.CONDITION, set(), cond_used)

        if isinstance(stmt.body, BlockStatement):
            for s in stmt.body.statements or []:
                self._process_statement(s)
        else:
            self._process_statement(stmt.body)

    def _process_for(self, stmt: ForStatement, line: int):
        """Process for loop."""
        # Init part may define variables
        if stmt.control and stmt.control.init:
            for init in (stmt.control.init if isinstance(stmt.control.init, list) else [stmt.control.init]):
                if isinstance(init, LocalVariableDeclaration):
                    self._process_var_decl(init, _find_line(init, self.source_lines))

        # Condition as control dependency source
        if stmt.control:
            cond_line = _find_line(stmt.control, self.source_lines)
            cond_used = set()
            if stmt.control.condition:
                cond_used = self._extract_identifiers(stmt.control.condition)
            if cond_used:
                cond_code = "for(...; " + _extract_node_code(self.source_lines, cond_line).split(';')[-1].strip().rstrip(')') + ")"
                self._add_statement(cond_line, cond_code, NodeType.CONDITION, set(), cond_used)

        # Body
        if isinstance(stmt.body, BlockStatement):
            for s in stmt.body.statements or []:
                self._process_statement(s)
        else:
            self._process_statement(stmt.body)

    def _process_do_while(self, stmt: DoStatement, line: int):
        """Process do-while loop."""
        cond_used = self._extract_identifiers(stmt.condition)
        cond_code = "while (" + _extract_node_code(self.source_lines, line).split('while')[-1].strip().rstrip(';') + ")"
        self._add_statement(line, cond_code, NodeType.CONDITION, set(), cond_used)

        if isinstance(stmt.body, BlockStatement):
            for s in stmt.body.statements or []:
                self._process_statement(s)
        else:
            self._process_statement(stmt.body)

    def _process_return(self, stmt: ReturnStatement, line: int):
        """Process return statement."""
        code = _extract_node_code(self.source_lines, line)
        used = set()
        if stmt.expression:
            used = self._extract_identifiers(stmt.expression)
        self._add_statement(line, code, NodeType.RETURN, set(), used)

    def _process_throw(self, stmt: ThrowStatement, line: int):
        """Process throw statement."""
        code = _extract_node_code(self.source_lines, line)
        used = self._extract_identifiers(stmt.expression)
        self._add_statement(line, code, NodeType.RETURN, set(), used)

    def _process_try(self, stmt: TryStatement, line: int):
        """Process try-catch block."""
        # Try block
        if isinstance(stmt.block, BlockStatement):
            for s in stmt.block.statements or []:
                self._process_statement(s)
        else:
            self._process_statement(stmt.block)

        # Catch blocks: treat catch parameter as definition
        for catch in stmt.catches or []:
            if hasattr(catch, 'parameter') and catch.parameter:
                catch_line = _find_line(catch.parameter, self.source_lines)
                param_name = catch.parameter.name
                self._add_statement(catch_line, f"catch ({param_name})",
                                   NodeType.DECLARATION, {param_name}, set())
            if isinstance(catch.block, BlockStatement):
                for s in catch.block.statements or []:
                    self._process_statement(s)

        # Finally block
        if stmt.finally_block:
            if isinstance(stmt.finally_block, BlockStatement):
                for s in stmt.finally_block.statements or []:
                    self._process_statement(s)

    def _process_switch(self, stmt: SwitchStatement, line: int):
        """Process switch statement."""
        cond_code = "switch (" + _extract_node_code(self.source_lines, line).split('(')[-1].rstrip(')') + ")"
        cond_used = self._extract_identifiers(stmt.expression)
        self._add_statement(line, cond_code, NodeType.CONDITION, set(), cond_used)

        for case in stmt.cases or []:
            if hasattr(case, 'statements'):
                for s in case.statements or []:
                    self._process_statement(s)


def parse_java_method(source_code: str, method_name: str = None) -> List[Tuple[int, str, NodeType, Set[str], Set[str]]]:
    """
    Parse a Java source file and extract statements from a method.

    Args:
        source_code: Complete Java source code (class with method(s))
        method_name: Name of the method to analyze. If None, analyzes the first method found.

    Returns:
        List of (line, code, node_type, defined_vars, used_vars) tuples.
    """
    # javalang expects a compilation unit; wrap if needed
    import re
    stripped = re.sub(r'/\*.*?\*/', '', source_code, flags=re.DOTALL)
    stripped = re.sub(r'//[^\n]*', '', stripped)
    if not stripped.strip().startswith(('package', 'import', 'class',
                                         'public', 'private', 'protected',
                                         'static', 'abstract', 'final',
                                         '@', 'interface', 'enum')):
        source_code = f"class Wrapper {{\n{source_code}\n}}"

    try:
        ast = javalang.parse.parse(source_code)
    except Exception:
        # If parsing fails, try wrapping more aggressively
        source_code = f"public class Wrapper {{ public void analyze() {{\n{source_code}\n}} }}"
        try:
            ast = javalang.parse.parse(source_code)
        except Exception as e:
            raise ValueError(f"Failed to parse Java source: {e}")

    # Find the target method
    for type_decl in ast.types:
        for member in type_decl.body or []:
            if isinstance(member, MethodDeclaration):
                if method_name is None or member.name == method_name:
                    analyzer = JavaMethodAnalyzer(source_code, member)
                    return analyzer.analyze_with_branches()

    raise ValueError(f"Method '{method_name}' not found in source code")


def parse_java_file(source_code: str) -> Dict[str, List[Tuple[int, str, NodeType, Set[str], Set[str]]]]:
    """
    Parse a Java source file and extract ALL methods.

    Returns:
        Dict mapping method_name → list of statement tuples.
    """
    result = {}

    # Strip block comments (/* ... */) and line comments (//) before
    # checking whether source is valid Java, so that files with
    # copyright headers are handled correctly.
    import re
    stripped = re.sub(r'/\*.*?\*/', '', source_code, flags=re.DOTALL)
    stripped = re.sub(r'//[^\n]*', '', stripped)
    if not stripped.strip().startswith(('package', 'import', 'class',
                                         'public', 'private', 'protected',
                                         'static', 'abstract', 'final',
                                         '@', 'interface', 'enum')):
        source_code = f"class Wrapper {{\n{source_code}\n}}"

    try:
        ast = javalang.parse.parse(source_code)
    except Exception as e:
        raise ValueError(f"Failed to parse Java source: {e}")

    for type_decl in ast.types:
        for member in type_decl.body or []:
            if isinstance(member, MethodDeclaration):
                analyzer = JavaMethodAnalyzer(source_code, member)
                result[member.name] = analyzer.analyze_with_branches()

    return result
