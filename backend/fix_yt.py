import ast
with open('media_controller.py', 'r', encoding='utf-8') as f:
    content = f.read()
tree = ast.parse(content)
func = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'youtube_play'), None)
if func is None:
    print("ERROR: youtube_play not found")
    exit(1)
lines = content.split('\n')
new_func = '''    def youtube_play(self, query: str) -> Dict:
        try:
            import pywhatkit
            print(f"[YouTube] Playing: {query}")
            pywhatkit.playonyt(query)
            return {"success": True, "message": f"YouTube pe '{query}' play kar diya"}
        except Exception as e:
            print(f"[YouTube] Error: {e}")
            return {"success": False, "error": str(e)}'''
new_lines = lines[:func.lineno-1] + new_func.split('\n') + lines[func.end_lineno:]
with open('media_controller.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))
print(f"REPLACED lines {func.lineno} to {func.end_lineno}")
