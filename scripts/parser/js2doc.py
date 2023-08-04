import os

import escodegen
import esprima


def find_files(directory):
    files_list = []
    for root, dirs, files in os.walk(directory):
        files_list.extend(
            os.path.join(root, file) for file in files if file.endswith('.js')
        )
    return files_list


def extract_functions(file_path):
    with open(file_path, 'r') as file:
        source_code = file.read()
        functions = {}
        tree = esprima.parseScript(source_code)
        for node in tree.body:
            if node.type == 'FunctionDeclaration':
                func_name = node.id.name if node.id else '<anonymous>'
                functions[func_name] = escodegen.generate(node)
            elif node.type == 'VariableDeclaration':
                for declaration in node.declarations:
                    if declaration.init and declaration.init.type == 'FunctionExpression':
                        func_name = declaration.id.name if declaration.id else '<anonymous>'
                        functions[func_name] = escodegen.generate(declaration.init)
            elif node.type == 'ClassDeclaration':
                for subnode in node.body.body:
                    if subnode.type == 'MethodDefinition':
                        func_name = subnode.key.name
                        functions[func_name] = escodegen.generate(subnode.value)
                    elif subnode.type == 'VariableDeclaration':
                        for declaration in subnode.declarations:
                            if declaration.init and declaration.init.type == 'FunctionExpression':
                                func_name = declaration.id.name if declaration.id else '<anonymous>'
                                functions[func_name] = escodegen.generate(declaration.init)
        return functions


def extract_classes(file_path):
    with open(file_path, 'r') as file:
        source_code = file.read()
        classes = {}
        tree = esprima.parseScript(source_code)
        for node in tree.body:
            if node.type == 'ClassDeclaration':
                class_name = node.id.name
                function_names = [
                    subnode.key.name
                    for subnode in node.body.body
                    if subnode.type == 'MethodDefinition'
                ]
                classes[class_name] = ", ".join(function_names)
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
