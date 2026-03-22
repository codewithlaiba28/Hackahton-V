from agents import function_tool

@function_tool
def test_no_parens():
    """Test without parens"""
    pass

@function_tool()
def test_with_parens():
    """Test with parens"""
    pass

print(f"No parens name: {getattr(test_no_parens, 'name', 'MISSING')}")
print(f"No parens type: {type(test_no_parens)}")
print(f"With parens name: {getattr(test_with_parens, 'name', 'MISSING')}")
print(f"With parens type: {type(test_with_parens)}")
