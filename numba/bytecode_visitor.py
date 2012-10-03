#! /usr/bin/env python
# ______________________________________________________________________

import opcode
from opcode_util import itercode

# ______________________________________________________________________

class BytecodeVisitor (object):
    opnames = [name.split('+')[0] for name in opcode.opname]

    def visit (self, co_obj):
        self.enter_code_object(co_obj)
        for i, op, arg in itercode(co_obj.co_code):
            self.visit_op(i, op, arg)
        return self.exit_code_object(co_obj)

    def enter_code_object (self, co_obj):
        pass

    def exit_code_object (self, co_obj):
        passe

    def visit_op (self, i, op, arg):
        return getattr(self, 'op_' + self.opnames[op])(i, op, arg)

    def op_BINARY_ADD (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BINARY_ADD")

    def op_BINARY_AND (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BINARY_AND")

    def op_BINARY_DIVIDE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BINARY_DIVIDE")

    def op_BINARY_FLOOR_DIVIDE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BINARY_FLOOR_DIVIDE")

    def op_BINARY_LSHIFT (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BINARY_LSHIFT")

    def op_BINARY_MODULO (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BINARY_MODULO")

    def op_BINARY_MULTIPLY (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BINARY_MULTIPLY")

    def op_BINARY_OR (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BINARY_OR")

    def op_BINARY_POWER (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BINARY_POWER")

    def op_BINARY_RSHIFT (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BINARY_RSHIFT")

    def op_BINARY_SUBSCR (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BINARY_SUBSCR")

    def op_BINARY_SUBTRACT (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BINARY_SUBTRACT")

    def op_BINARY_TRUE_DIVIDE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BINARY_TRUE_DIVIDE")

    def op_BINARY_XOR (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BINARY_XOR")

    def op_BREAK_LOOP (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BREAK_LOOP")

    def op_BUILD_CLASS (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BUILD_CLASS")

    def op_BUILD_LIST (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BUILD_LIST")

    def op_BUILD_MAP (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BUILD_MAP")

    def op_BUILD_SET (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BUILD_SET")

    def op_BUILD_SLICE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BUILD_SLICE")

    def op_BUILD_TUPLE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_BUILD_TUPLE")

    def op_CALL_FUNCTION (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_CALL_FUNCTION")

    def op_CALL_FUNCTION_KW (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_CALL_FUNCTION_KW")

    def op_CALL_FUNCTION_VAR (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_CALL_FUNCTION_VAR")

    def op_CALL_FUNCTION_VAR_KW (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_CALL_FUNCTION_VAR_KW")

    def op_COMPARE_OP (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_COMPARE_OP")

    def op_CONTINUE_LOOP (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_CONTINUE_LOOP")

    def op_DELETE_ATTR (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_DELETE_ATTR")

    def op_DELETE_DEREF (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_DELETE_DEREF")

    def op_DELETE_FAST (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_DELETE_FAST")

    def op_DELETE_GLOBAL (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_DELETE_GLOBAL")

    def op_DELETE_NAME (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_DELETE_NAME")

    def op_DELETE_SLICE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_DELETE_SLICE")

    def op_DELETE_SUBSCR (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_DELETE_SUBSCR")

    def op_DUP_TOP (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_DUP_TOP")

    def op_DUP_TOPX (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_DUP_TOPX")

    def op_DUP_TOP_TWO (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_DUP_TOP_TWO")

    def op_END_FINALLY (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_END_FINALLY")

    def op_EXEC_STMT (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_EXEC_STMT")

    def op_EXTENDED_ARG (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_EXTENDED_ARG")

    def op_FOR_ITER (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_FOR_ITER")

    def op_GET_ITER (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_GET_ITER")

    def op_IMPORT_FROM (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_IMPORT_FROM")

    def op_IMPORT_NAME (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_IMPORT_NAME")

    def op_IMPORT_STAR (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_IMPORT_STAR")

    def op_INPLACE_ADD (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_INPLACE_ADD")

    def op_INPLACE_AND (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_INPLACE_AND")

    def op_INPLACE_DIVIDE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_INPLACE_DIVIDE")

    def op_INPLACE_FLOOR_DIVIDE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_INPLACE_FLOOR_DIVIDE")

    def op_INPLACE_LSHIFT (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_INPLACE_LSHIFT")

    def op_INPLACE_MODULO (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_INPLACE_MODULO")

    def op_INPLACE_MULTIPLY (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_INPLACE_MULTIPLY")

    def op_INPLACE_OR (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_INPLACE_OR")

    def op_INPLACE_POWER (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_INPLACE_POWER")

    def op_INPLACE_RSHIFT (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_INPLACE_RSHIFT")

    def op_INPLACE_SUBTRACT (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_INPLACE_SUBTRACT")

    def op_INPLACE_TRUE_DIVIDE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_INPLACE_TRUE_DIVIDE")

    def op_INPLACE_XOR (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_INPLACE_XOR")

    def op_JUMP_ABSOLUTE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_JUMP_ABSOLUTE")

    def op_JUMP_FORWARD (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_JUMP_FORWARD")

    def op_JUMP_IF_FALSE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_JUMP_IF_FALSE")

    def op_JUMP_IF_FALSE_OR_POP (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_JUMP_IF_FALSE_OR_POP")

    def op_JUMP_IF_TRUE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_JUMP_IF_TRUE")

    def op_JUMP_IF_TRUE_OR_POP (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_JUMP_IF_TRUE_OR_POP")

    def op_LIST_APPEND (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_LIST_APPEND")

    def op_LOAD_ATTR (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_LOAD_ATTR")

    def op_LOAD_BUILD_CLASS (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_LOAD_BUILD_CLASS")

    def op_LOAD_CLOSURE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_LOAD_CLOSURE")

    def op_LOAD_CONST (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_LOAD_CONST")

    def op_LOAD_DEREF (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_LOAD_DEREF")

    def op_LOAD_FAST (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_LOAD_FAST")

    def op_LOAD_GLOBAL (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_LOAD_GLOBAL")

    def op_LOAD_LOCALS (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_LOAD_LOCALS")

    def op_LOAD_NAME (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_LOAD_NAME")

    def op_MAKE_CLOSURE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_MAKE_CLOSURE")

    def op_MAKE_FUNCTION (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_MAKE_FUNCTION")

    def op_MAP_ADD (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_MAP_ADD")

    def op_NOP (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_NOP")

    def op_POP_BLOCK (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_POP_BLOCK")

    def op_POP_EXCEPT (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_POP_EXCEPT")

    def op_POP_JUMP_IF_FALSE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_POP_JUMP_IF_FALSE")

    def op_POP_JUMP_IF_TRUE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_POP_JUMP_IF_TRUE")

    def op_POP_TOP (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_POP_TOP")

    def op_PRINT_EXPR (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_PRINT_EXPR")

    def op_PRINT_ITEM (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_PRINT_ITEM")

    def op_PRINT_ITEM_TO (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_PRINT_ITEM_TO")

    def op_PRINT_NEWLINE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_PRINT_NEWLINE")

    def op_PRINT_NEWLINE_TO (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_PRINT_NEWLINE_TO")

    def op_RAISE_VARARGS (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_RAISE_VARARGS")

    def op_RETURN_VALUE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_RETURN_VALUE")

    def op_ROT_FOUR (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_ROT_FOUR")

    def op_ROT_THREE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_ROT_THREE")

    def op_ROT_TWO (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_ROT_TWO")

    def op_SETUP_EXCEPT (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_SETUP_EXCEPT")

    def op_SETUP_FINALLY (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_SETUP_FINALLY")

    def op_SETUP_LOOP (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_SETUP_LOOP")

    def op_SETUP_WITH (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_SETUP_WITH")

    def op_SET_ADD (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_SET_ADD")

    def op_SLICE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_SLICE")

    def op_STOP_CODE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_STOP_CODE")

    def op_STORE_ATTR (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_STORE_ATTR")

    def op_STORE_DEREF (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_STORE_DEREF")

    def op_STORE_FAST (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_STORE_FAST")

    def op_STORE_GLOBAL (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_STORE_GLOBAL")

    def op_STORE_LOCALS (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_STORE_LOCALS")

    def op_STORE_MAP (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_STORE_MAP")

    def op_STORE_NAME (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_STORE_NAME")

    def op_STORE_SLICE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_STORE_SLICE")

    def op_STORE_SUBSCR (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_STORE_SUBSCR")

    def op_UNARY_CONVERT (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_UNARY_CONVERT")

    def op_UNARY_INVERT (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_UNARY_INVERT")

    def op_UNARY_NEGATIVE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_UNARY_NEGATIVE")

    def op_UNARY_NOT (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_UNARY_NOT")

    def op_UNARY_POSITIVE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_UNARY_POSITIVE")

    def op_UNPACK_EX (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_UNPACK_EX")

    def op_UNPACK_SEQUENCE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_UNPACK_SEQUENCE")

    def op_WITH_CLEANUP (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_WITH_CLEANUP")

    def op_YIELD_VALUE (self, i, op, arg):
        raise NotImplementedError("BytecodeVisitor.op_YIELD_VALUE")

# ______________________________________________________________________
# End of bytecode_visitor.py
