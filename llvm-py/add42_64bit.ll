@.str = private constant [2 x i8] c"l\00"

define i8* @add42(i8* %self, i8* %args) nounwind {
Entry:
  %value = alloca i64, align 8
  store i64 0, i64* %value
  %0 = call i32 (i8*, i8*, ...)* @PyArg_ParseTuple(i8* %args, i8* getelementptr inbounds ([2 x i8]* @.str, i32 0, i32 0), i64* %value)
  %1 = icmp ne i32 %0, 0
  br i1 %1, label %ArgsOk, label %Exit

ArgsOk:
  %2 = load i64* %value
  %3 = add i64 %2, 42
  %4 = call i8* @PyInt_FromLong(i64 %3)
  br label %Exit

Exit:
  %5 = phi i8* [ null, %Entry], [ %4, %ArgsOk ]
  ret i8* %5
}

declare i8* @PyInt_FromLong(i64)

declare i32 @PyArg_ParseTuple(i8*, i8*, ...)
