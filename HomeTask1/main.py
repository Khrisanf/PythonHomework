from fastapi import FastAPI
from pydantic import BaseModel
import ast
import operator

app = FastAPI()

#Глобальная переменная для хранения выражения
current_expression = ""

#Словарь операторов для безопасного вычисления выражений
operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

class Expression(BaseModel):
    expression: str

def eval_expr(expr):
    """Безопасный парсер математического выражения."""
    try:
        tree = ast.parse(expr, mode='eval')
        return eval_ast(tree.body)
    except Exception as e:
        return str(e)

def eval_ast(node):
    """Рекурсивная обработка AST-дерева выражения."""
    if isinstance(node, ast.BinOp):
        left = eval_ast(node.left)
        right = eval_ast(node.right)
        op_type = type(node.op)

        if op_type in operators:
            return operators[op_type](left, right)
        else:
            raise ValueError(f"Недопустимый оператор: {op_type}")

    elif isinstance(node, ast.Num):  
        return node.n
    elif isinstance(node, ast.UnaryOp):  
        return -eval_ast(node.operand)
    else:
        raise ValueError("Некорректное выражение")

@app.post("/add_expression")
def add_expression(expr: Expression):
    """Добавляет выражение в глобальную переменную."""
    global current_expression
    current_expression = expr.expression
    return {"message": "Выражение сохранено", "expression": current_expression}

@app.get("/get_expression")
def get_expression():
    """Возвращает текущее сохранённое выражение."""
    return {"expression": current_expression}

@app.get("/execute")
def execute_expression():
    """Выполняет сохранённое выражение."""
    global current_expression
    if not current_expression:
        return {"error": "Нет сохранённого выражения"}
    
    result = eval_expr(current_expression)
    return {"expression": current_expression, "result": result}

@app.get("/calculate")
def calculate(a: float, op: str, b: float):
    """Выполняет базовые математические операции."""
    try:
        if op == "+":
            return {"result": a + b}
        elif op == "-":
            return {"result": a - b}
        elif op == "*":
            return {"result": a * b}
        elif op == "/":
            if b == 0:
                return {"error": "Деление на ноль!"}
            return {"result": a / b}
        else:
            return {"error": "Неподдерживаемая операция"}
    except Exception as e:
        return {"error": str(e)}
