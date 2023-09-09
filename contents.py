import os
import ast

def remove_docstrings_and_comments(source):
    module = ast.parse(source)

    class DocstringAndCommentRemover(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            node.body = [n for n in node.body if not isinstance(n, ast.Expr) or not isinstance(n.value, ast.Str)]
            return self.generic_visit(node)

        def visit_ClassDef(self, node):
            node.body = [n for n in node.body if not isinstance(n, ast.Expr) or not isinstance(n.value, ast.Str)]
            return self.generic_visit(node)

        def visit_Module(self, node):
            node.body = [n for n in node.body if not isinstance(n, ast.Expr) or not isinstance(n.value, ast.Str)]
            return self.generic_visit(node)

    module = DocstringAndCommentRemover().visit(module)
    return ast.unparse(module)

def write_files_content_to_txt(dir_path, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for root, dirs, files in os.walk(dir_path):
            if '.venv' in dirs:
                dirs.remove('.venv')  # исключаем папку .venv из обхода

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    output_file.write(f'Path: {file_path}\n')

                    with open(file_path, 'r', encoding='utf-8') as input_file:  # указываем кодировку файлов
                        source_code = input_file.read()
                        clean_source_code = remove_docstrings_and_comments(source_code)
                        output_file.write(clean_source_code)
                        output_file.write('\n')

dir_path = './'  # Замените на путь до вашей папки
output_file_path = 'output.txt'  # Замените на путь до выходного файла, если требуется

write_files_content_to_txt(dir_path, output_file_path)
