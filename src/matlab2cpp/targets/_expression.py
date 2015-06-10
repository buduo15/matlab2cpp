"""
Expressions

Nodes
-----
Expr : General expression
    Take the following form:
        Band, Bor, Colon, Ctranspose, Div, Eldiv, Elexp, Elmul,
        Elrdiv, End, Eq, Exp, Float, Ge, Get, Get2, Get3, Gt,
        Ifloat, Iint, Int, Land, Lor, Lt, Matrix, Minus, Mul, Ne,
        Neg, Not, Paren, Plus, Rdiv, String, Transpose, Var

Band : Bit-vise And-operator
    Example: "x && y"
    Contains: Expr, Expr, ...

Bor : Bit-vise Or-operator
    Example: "x || y"
    Contains: Expr, Expr, ...

Colon : Colon
    Example: "x:y"
    Example: "x:y:z"
    Contains: Expr, Expr, (Expr)

Ctranspose : Ctranspose
    Example: "x'"
    Contains: Expr

Div : Division
    Example: "x / y"
    Contains: Expr, Expr, ...

Eldiv : Element-wise division
    Example: "x ./ y"
    Contains: Expr, Expr, ...

Elexp : Element-wise exponent
    Example: "x .^ y"
    Contains: Expr, Expr, ...

Elmul : Element-wise multiplication
    Example: "x .* y"
    Contains: Expr, Expr, ...

Elrdiv : Element-wise right division
    Example: "x .\ y"
    Contains: Expr, Expr, ...

End : Special charracter: last element in range/array
    Example: "y(end)"

Eq : Equate (Truth-value)
    Example: "x == y"
    Contains: Expr, Expr

Exp : Exponent
    Example: "x ^ y"
    Contains: Expr, Expr, ...

Ge : Greater or equal
    Example: "x >= y"
    Contains: Expr

Gt : Greater than
    Example: "x > y"
    Contains: Expr, Expr

Land : Logical And
    Example: "x and y"
    Contains: Expr

Lor : Logical Or
    Example: "x or y"
    Contains: Expr

Lt : Lt
    Example: "x < y"
    Contains: Expr, Expr

Minus : Subtraction
    Example: "x - y"
    Contains: Expr, Expr, ...

Mul : Multiplication
    Example: "x * y"
    Contains: Expr, Expr, ...

Ne : Not equal
    Example: "x <> y"
    Contains: Expr, Expr

Neg : Negative
    Example: "-y"
    Contains: Expr

Not : Negation
    Example: "not y"
    Contains: Expr

Paren : Parenthesis
    Example: "(y)"
    Contains: Expr

Plus : Addition
    Example: "x + y"
    Contains: Expr, Expr, ...

Rdiv : Right devision
    Example: "x \ y"
    Contains: Expr

Transpose : Transpose
    Example: "y.'"
    Contains: Expr

Break : Break
    Example: "break"

Return : Return
    Example: "return"
"""

Expr = "%(0)s"
Gets = "", ", ", ""
Paren = "(%(0)s)"

def End(node):

    pnode = node
    while pnode.parent["class"] not in \
            ("Get", "Cget", "Nget", "Fget", "Sget",
            "Set", "Cset", "Nset", "Fset", "Sset", "Block"):
        pnode = pnode.parent

    if pnode.cls == "Block":
        return "end"

    index = pnode.parent.children.index(pnode)
    name = pnode = pnode.parent["name"]

    if index == 0:
        return name + ".n_rows"
    elif index == 1:
        return name + ".n_cols"
    elif index == 2:
        return name + ".n_slices"

Break = "break"

def Return(node):
    func = node.func
    if func["backend"] == "func_returns":
        return "return"
    if func["backend"] == "func_lambda":
        return "return _retval"

    return "return " + func[1][0]["name"]



# simple operators
def Mul(node):
    return "", "*", ""

def Elmul(node):
    return "", ".*", ""

def Plus(node):
    return "", "+", ""

def Minus(node):
    return "", "-", ""

Gt      = "", ">", ""
Ge      = "", ">=", ""
Lt      = "", "<", ""
Le      = "", "<=", ""
Ne      = "", "~=", ""
Eq      = "", "==", ""
Band    = "", "&&", ""
Land    = "", "&", ""
Bor     = "", "||", ""
Lor     = "", "|", ""
Div     = "", "/", ""

def Eldiv(node):
    out = ""
    for child in node[::-1]:
        out = out + "/" + str(child)
    return out[1:]

def Div(node):
    if 0 in {n.dim for n in node}:
        return Eldiv(node)
    out = str(node[0])

    for child in node[1:]:
        if child.dim == 3:
            out = "arma::solve(" +out + ", " + str(child) + ")"
        else:
            out = str(child) + "/" + out

    return out

def Exp(node):
    out = str(node[0])
    for child in node[1:]:
        out = "pow(" + str(out) + "," + str(child) + ")"
    return out
def Elexp(node):
    out = str(node[0])
    for child in node[1:]:
        out = "pow(" + str(out) + "," + str(child) + ")"
    return out

All = "span::all"
Neg = "-(", "", ")"
Not = "not ", "", ""

def Transpose(node):
    if not node.num:
        return "arma::trans(", "", ")"
    if node.dim == 1:
        node.dim = 2
    elif node.dim == 2:
        node.dim = 1
    return "arma::trans(", "", ")"

def Ctranspose(node):
    if not node.num:
        return "arma::strans(", "", ")"
    if node.dim == 2:
        node.dim = 3
    elif node.dim == 3:
        node.dim = 2
    return "arma::strans(", "", ")"

def Rdiv(node):
    return "", "/", ""

def Elrdiv(node):
    children = map(str, node[:])[::-1]
    return "/".join(children)

def Colon(node):

    parent = node.parent

    if len(node) == 2:

        if parent["class"] in ("Get", "Cget", "Nget", "Fget", "Sget",
                "Set", "Cset", "Nset", "Fset", "Sset") and parent.num:
            node.type = "uvec"
            return "span(%(0)s-1, %(1)s-1)"

        elif node.parent["class"] == "Assign" and not parent.mem:
            node.type = "ivec"
            return "span(%(0)s, %(1)s)"

        node.type = "ivec"
        return "span(%(0)s, %(1)s)"


    if len(node) == 3:

        if parent["class"] in ("Get", "Cget", "Nget", "Fget", "Sget",
                "Set", "Cset", "Nset", "Fset", "Sset") and parent.num:
            node.type = "uvec"
            return "span(%(0)s-1, %(1)s, %(2)s-1)"

        elif node.parent["class"] == "Assign" and not parent.mem:
            node.type = "ivec"
            return "span(%(0)s, %(1)s, %(2)s)"

        node.type = "ivec"
        return "span(%(0)s, %(1)s, %(2)s)"


    return "", ":", ""