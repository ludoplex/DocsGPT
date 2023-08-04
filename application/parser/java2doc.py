import os

import javalang


def find_files(directory):
    files_list = []
    for root, dirs, files in os.walk(directory):
        files_list.extend(
            os.path.join(root, file)
            for file in files
            if file.endswith('.java')
        )
    return files_list


def extract_functions(file_path):
    with open(file_path, "r") as file:
        java_code = file.read()
        methods = {}
        tree = javalang.parse.parse(java_code)
        for _, node in tree.filter(javalang.tree.MethodDeclaration):
            method_name = node.name
            start_line = node.position.line - 1
            end_line = start_line
            brace_count = 0
            for line in java_code.splitlines()[start_line:]:
                end_line += 1
                brace_count += line.count("{") - line.count("}")
                if brace_count == 0:
                    break
            method_source_code = "\n".join(java_code.splitlines()[start_line:end_line])
            methods[method_name] = method_source_code
    return methods


def extract_classes(file_path):
    with open(file_path, 'r') as file:
        source_code = file.read()
        classes = {}
        tree = javalang.parse.parse(source_code)
        for class_decl in tree.types:
            class_name = class_decl.name
            declarations = []
            for field_decl in class_decl.fields:
                field_name = field_decl.declarators[0].name
                field_type = field_decl.type.name
                declarations.append(f"{field_type} {field_name}")
            methods = [method_decl.name for method_decl in class_decl.methods]
            class_string = "Declarations: " + ", ".join(declarations) + "\n  Method name: " + ", ".join(methods)
            classes[class_name] = class_string
    return classes


def extract_functions_and_classes(directory):
    files = find_files(directory)
    functions_dict = {}
    classes_dict = {}
    for file in files:
        if functions := extract_functions(file):
            functions_dict[file] = functions
        if classes := extract_classes(file):
            classes_dict[file] = classes
    return functions_dict, classes_dict
