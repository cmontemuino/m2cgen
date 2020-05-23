from m2cgen import ast
from m2cgen.interpreters import VisualBasicInterpreter
from tests import utils


def test_if_expr():
    expr = ast.IfExpr(
        ast.CompExpr(ast.NumVal(1), ast.FeatureRef(0), ast.CompOpType.EQ),
        ast.NumVal(2),
        ast.NumVal(3))

    expected_code = """
Module Model
Function Score(ByRef inputVector() As Double) As Double
    Dim var0 As Double
    If (1) = (inputVector(0)) Then
        var0 = 2
    Else
        var0 = 3
    End If
    Score = var0
End Function
End Module
"""

    interpreter = VisualBasicInterpreter()
    utils.assert_code_equal(interpreter.interpret(expr), expected_code)


def test_bin_num_expr():
    expr = ast.BinNumExpr(
        ast.BinNumExpr(
            ast.FeatureRef(0), ast.NumVal(-2), ast.BinNumOpType.DIV),
        ast.NumVal(2),
        ast.BinNumOpType.MUL)

    expected_code = """
Module Model
Function Score(ByRef inputVector() As Double) As Double
    Score = ((inputVector(0)) / (-2)) * (2)
End Function
End Module
"""

    interpreter = VisualBasicInterpreter()
    utils.assert_code_equal(interpreter.interpret(expr), expected_code)


def test_dependable_condition():
    left = ast.BinNumExpr(
        ast.IfExpr(
            ast.CompExpr(ast.NumVal(1),
                         ast.NumVal(1),
                         ast.CompOpType.EQ),
            ast.NumVal(1),
            ast.NumVal(2)),
        ast.NumVal(2),
        ast.BinNumOpType.ADD)

    right = ast.BinNumExpr(ast.NumVal(1), ast.NumVal(2), ast.BinNumOpType.DIV)
    bool_test = ast.CompExpr(left, right, ast.CompOpType.GTE)

    expr = ast.IfExpr(bool_test, ast.NumVal(1), ast.FeatureRef(0))

    expected_code = """
Module Model
Function Score(ByRef inputVector() As Double) As Double
    Dim var0 As Double
    Dim var1 As Double
    If (1) = (1) Then
        var1 = 1
    Else
        var1 = 2
    End If
    If ((var1) + (2)) >= ((1) / (2)) Then
        var0 = 1
    Else
        var0 = inputVector(0)
    End If
    Score = var0
End Function
End Module
"""

    interpreter = VisualBasicInterpreter()
    utils.assert_code_equal(interpreter.interpret(expr), expected_code)


def test_nested_condition():
    left = ast.BinNumExpr(
        ast.IfExpr(
            ast.CompExpr(ast.NumVal(1),
                         ast.NumVal(1),
                         ast.CompOpType.EQ),
            ast.NumVal(1),
            ast.NumVal(2)),
        ast.NumVal(2),
        ast.BinNumOpType.ADD)

    bool_test = ast.CompExpr(ast.NumVal(1), left, ast.CompOpType.EQ)

    expr_nested = ast.IfExpr(bool_test, ast.FeatureRef(2), ast.NumVal(2))

    expr = ast.IfExpr(bool_test, expr_nested, ast.NumVal(2))

    expected_code = """
Module Model
Function Score(ByRef inputVector() As Double) As Double
    Dim var0 As Double
    Dim var1 As Double
    If (1) = (1) Then
        var1 = 1
    Else
        var1 = 2
    End If
    If (1) = ((var1) + (2)) Then
        Dim var2 As Double
        If (1) = (1) Then
            var2 = 1
        Else
            var2 = 2
        End If
        If (1) = ((var2) + (2)) Then
            var0 = inputVector(2)
        Else
            var0 = 2
        End If
    Else
        var0 = 2
    End If
    Score = var0
End Function
End Module
"""

    interpreter = VisualBasicInterpreter()
    utils.assert_code_equal(interpreter.interpret(expr), expected_code)


def test_module_name():
    expr = ast.NumVal(1)

    expected_code = """
Module Test
Function Score(ByRef inputVector() As Double) As Double
    Score = 1
End Function
End Module
"""

    interpreter = VisualBasicInterpreter(module_name="Test")
    utils.assert_code_equal(interpreter.interpret(expr), expected_code)


def test_raw_array():
    expr = ast.VectorVal([ast.NumVal(3), ast.NumVal(4)])

    expected_code = """
Module Model
Function Score(ByRef inputVector() As Double) As Double()
    Dim var0(1) As Double
    var0(0) = 3
    var0(1) = 4
    Score = var0
End Function
End Module
"""

    interpreter = VisualBasicInterpreter()
    utils.assert_code_equal(interpreter.interpret(expr), expected_code)


def test_multi_output():
    expr = ast.IfExpr(
        ast.CompExpr(
            ast.NumVal(1),
            ast.NumVal(1),
            ast.CompOpType.EQ),
        ast.VectorVal([ast.NumVal(1), ast.NumVal(2)]),
        ast.VectorVal([ast.NumVal(3), ast.NumVal(4)]))

    expected_code = """
Module Model
Function Score(ByRef inputVector() As Double) As Double()
    Dim var0() As Double
    If (1) = (1) Then
        Dim var1(1) As Double
        var1(0) = 1
        var1(1) = 2
        var0 = var1
    Else
        Dim var2(1) As Double
        var2(0) = 3
        var2(1) = 4
        var0 = var2
    End If
    Score = var0
End Function
End Module
"""

    interpreter = VisualBasicInterpreter()
    utils.assert_code_equal(interpreter.interpret(expr), expected_code)


def test_bin_vector_expr():
    expr = ast.BinVectorExpr(
        ast.VectorVal([ast.NumVal(1), ast.NumVal(2)]),
        ast.VectorVal([ast.NumVal(3), ast.NumVal(4)]),
        ast.BinNumOpType.ADD)

    expected_code = """
Module Model
Function AddVectors(ByRef v1() As Double, ByRef v2() As Double) As Double()
    Dim resLength As Integer
    resLength = UBound(v1) - LBound(v1)
    Dim result() As Double
    ReDim result(resLength)

    Dim i As Integer
    For i = LBound(v1) To UBound(v1)
        result(i) = v1(i) + v2(i)
    Next i

    AddVectors = result
End Function
Function MulVectorNumber(ByRef v1() As Double, ByVal num As Double) As Double()
    Dim resLength As Integer
    resLength = UBound(v1) - LBound(v1)
    Dim result() As Double
    ReDim result(resLength)

    Dim i As Integer
    For i = LBound(v1) To UBound(v1)
        result(i) = v1(i) * num
    Next i

    MulVectorNumber = result
End Function
Function Score(ByRef inputVector() As Double) As Double()
    Dim var0(1) As Double
    var0(0) = 1
    var0(1) = 2
    Dim var1(1) As Double
    var1(0) = 3
    var1(1) = 4
    Score = AddVectors(var0, var1)
End Function
End Module
"""

    interpreter = VisualBasicInterpreter()
    utils.assert_code_equal(interpreter.interpret(expr), expected_code)


def test_bin_vector_num_expr():
    expr = ast.BinVectorNumExpr(
        ast.VectorVal([ast.NumVal(1), ast.NumVal(2)]),
        ast.NumVal(1),
        ast.BinNumOpType.MUL)

    expected_code = """
Module Model
Function AddVectors(ByRef v1() As Double, ByRef v2() As Double) As Double()
    Dim resLength As Integer
    resLength = UBound(v1) - LBound(v1)
    Dim result() As Double
    ReDim result(resLength)

    Dim i As Integer
    For i = LBound(v1) To UBound(v1)
        result(i) = v1(i) + v2(i)
    Next i

    AddVectors = result
End Function
Function MulVectorNumber(ByRef v1() As Double, ByVal num As Double) As Double()
    Dim resLength As Integer
    resLength = UBound(v1) - LBound(v1)
    Dim result() As Double
    ReDim result(resLength)

    Dim i As Integer
    For i = LBound(v1) To UBound(v1)
        result(i) = v1(i) * num
    Next i

    MulVectorNumber = result
End Function
Function Score(ByRef inputVector() As Double) As Double()
    Dim var0(1) As Double
    var0(0) = 1
    var0(1) = 2
    Score = MulVectorNumber(var0, 1)
End Function
End Module
"""

    interpreter = VisualBasicInterpreter()
    utils.assert_code_equal(interpreter.interpret(expr), expected_code)


def test_exp_expr():
    expr = ast.ExpExpr(ast.NumVal(1.0))

    expected_code = """
Module Model
Function Score(ByRef inputVector() As Double) As Double
    Score = Math.Exp(1.0)
End Function
End Module
"""

    interpreter = VisualBasicInterpreter()
    utils.assert_code_equal(interpreter.interpret(expr), expected_code)


def test_pow_expr():
    expr = ast.PowExpr(ast.NumVal(2.0), ast.NumVal(3.0))

    expected_code = """
Module Model
Function Score(ByRef inputVector() As Double) As Double
    Score = (2.0) ^ (3.0)
End Function
End Module
"""

    interpreter = VisualBasicInterpreter()
    utils.assert_code_equal(interpreter.interpret(expr), expected_code)


def test_sqrt_expr():
    expr = ast.SqrtExpr(ast.NumVal(2.0))

    expected_code = """
Module Model
Function Score(ByRef inputVector() As Double) As Double
    Score = (2.0) ^ (0.5)
End Function
End Module
"""

    interpreter = VisualBasicInterpreter()
    utils.assert_code_equal(interpreter.interpret(expr), expected_code)


def test_tanh_expr():
    expr = ast.TanhExpr(ast.NumVal(2.0))

    expected_code = """
Module Model
Function Tanh(ByVal number As Double) As Double
    If number > 44.0 Then  ' exp(2*x) <= 2^127
        Tanh = 1.0
        Exit Function
    End If
    If number < -44.0 Then
        Tanh = -1.0
        Exit Function
    End If
    Tanh = (Math.Exp(2 * number) - 1) / (Math.Exp(2 * number) + 1)
End Function
Function Score(ByRef inputVector() As Double) As Double
    Score = Tanh(2.0)
End Function
End Module
"""

    interpreter = VisualBasicInterpreter()
    utils.assert_code_equal(interpreter.interpret(expr), expected_code)


def test_log_expr():
    expr = ast.LogExpr(ast.NumVal(2.0))

    expected_code = """
Module Model
Function Score(ByRef inputVector() As Double) As Double
    Score = Math.Log(2.0)
End Function
End Module
"""

    interpreter = VisualBasicInterpreter()
    utils.assert_code_equal(interpreter.interpret(expr), expected_code)


def test_log1p_expr():
    expr = ast.Log1pExpr(ast.NumVal(2.0))

    expected_code = """
Module Model
Function ChebyshevBroucke(ByVal x As Double, _
                          ByRef coeffs() As Double) As Double
    Dim b2 as Double
    Dim b1 as Double
    Dim b0 as Double
    Dim x2 as Double
    b2 = 0.0
    b1 = 0.0
    b0 = 0.0
    x2 = x * 2
    Dim i as Integer
    For i = UBound(coeffs) - 1 To 0 Step -1
        b2 = b1
        b1 = b0
        b0 = x2 * b1 - b2 + coeffs(i)
    Next i
    ChebyshevBroucke = (b0 - b2) * 0.5
End Function
Function Log1p(ByVal x As Double) As Double
    If x = 0.0 Then
        Log1p = 0.0
        Exit Function
    End If
    If x = -1.0 Then
        On Error Resume Next
        Log1p = -1.0 / 0.0
        Exit Function
    End If
    If x < -1.0 Then
        On Error Resume Next
        Log1p = 0.0 / 0.0
        Exit Function
    End If
    Dim xAbs As Double
    xAbs = Math.Abs(x)
    If xAbs < 0.5 * 4.94065645841247e-324 Then
        Log1p = x
        Exit Function
    End If
    If (x > 0.0 AND x < 1e-8) OR (x > -1e-9 AND x < 0.0) Then
        Log1p = x * (1.0 - x * 0.5)
        Exit Function
    End If
    If xAbs < 0.375 Then
        Dim coeffs(22) As Double
        coeffs(0) = 0.10378693562743769800686267719098e+1
        coeffs(1) = -0.13364301504908918098766041553133e+0
        coeffs(2) = 0.19408249135520563357926199374750e-1
        coeffs(3) = -0.30107551127535777690376537776592e-2
        coeffs(4) = 0.48694614797154850090456366509137e-3
        coeffs(5) = -0.81054881893175356066809943008622e-4
        coeffs(6) = 0.13778847799559524782938251496059e-4
        coeffs(7) = -0.23802210894358970251369992914935e-5
        coeffs(8) = 0.41640416213865183476391859901989e-6
        coeffs(9) = -0.73595828378075994984266837031998e-7
        coeffs(10) = 0.13117611876241674949152294345011e-7
        coeffs(11) = -0.23546709317742425136696092330175e-8
        coeffs(12) = 0.42522773276034997775638052962567e-9
        coeffs(13) = -0.77190894134840796826108107493300e-10
        coeffs(14) = 0.14075746481359069909215356472191e-10
        coeffs(15) = -0.25769072058024680627537078627584e-11
        coeffs(16) = 0.47342406666294421849154395005938e-12
        coeffs(17) = -0.87249012674742641745301263292675e-13
        coeffs(18) = 0.16124614902740551465739833119115e-13
        coeffs(19) = -0.29875652015665773006710792416815e-14
        coeffs(20) = 0.55480701209082887983041321697279e-15
        coeffs(21) = -0.10324619158271569595141333961932e-15
        Log1p = x * (1.0 - x * ChebyshevBroucke(x / 0.375, coeffs))
        Exit Function
    End If
    Log1p = Math.log(1.0 + x)
End Function
Function Score(ByRef inputVector() As Double) As Double
    Score = Log1p(2.0)
End Function
End Module
"""

    interpreter = VisualBasicInterpreter()
    utils.assert_code_equal(interpreter.interpret(expr), expected_code)


def test_reused_expr():
    reused_expr = ast.ExpExpr(ast.NumVal(1.0), to_reuse=True)
    expr = ast.BinNumExpr(reused_expr, reused_expr, ast.BinNumOpType.DIV)

    expected_code = """
Module Model
Function Score(ByRef inputVector() As Double) As Double
    Dim var0 As Double
    var0 = Math.Exp(1.0)
    Score = (var0) / (var0)
End Function
End Module
"""

    interpreter = VisualBasicInterpreter()
    utils.assert_code_equal(interpreter.interpret(expr), expected_code)
