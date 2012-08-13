; ModuleID = 'test_c99_complex.c'
;target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64-S128"
;target triple = "x86_64-unknown-linux-gnu"

%struct.test_complex_t = type { double, double }

@.str = private unnamed_addr constant [22 x i8] c"test_fn(): %lg%+lgj\0A\0A\00", align 1

define { double, double } @cidentity(double %in_val.coerce0, double %in_val.coerce1) nounwind uwtable {
entry:
  %retval = alloca { double, double }, align 8
  %in_val = alloca { double, double }, align 8
  %0 = getelementptr { double, double }* %in_val, i32 0, i32 0
  store double %in_val.coerce0, double* %0
  %1 = getelementptr { double, double }* %in_val, i32 0, i32 1
  store double %in_val.coerce1, double* %1
  %in_val.realp = getelementptr inbounds { double, double }* %in_val, i32 0, i32 0
  %in_val.real = load double* %in_val.realp
  %in_val.imagp = getelementptr inbounds { double, double }* %in_val, i32 0, i32 1
  %in_val.imag = load double* %in_val.imagp
  %real = getelementptr inbounds { double, double }* %retval, i32 0, i32 0
  %imag = getelementptr inbounds { double, double }* %retval, i32 0, i32 1
  store double %in_val.real, double* %real
  store double %in_val.imag, double* %imag
  %2 = load { double, double }* %retval
  ret { double, double } %2
}

define { double, double } @cidentity2(double %in_val.coerce0, double %in_val.coerce1) nounwind uwtable {
entry:
  %retval = alloca %struct.test_complex_t, align 8
  %in_val = alloca %struct.test_complex_t, align 8
  %0 = bitcast %struct.test_complex_t* %in_val to { double, double }*
  %1 = getelementptr { double, double }* %0, i32 0, i32 0
  store double %in_val.coerce0, double* %1
  %2 = getelementptr { double, double }* %0, i32 0, i32 1
  store double %in_val.coerce1, double* %2
  %3 = bitcast %struct.test_complex_t* %retval to i8*
  %4 = bitcast %struct.test_complex_t* %in_val to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* %3, i8* %4, i64 16, i32 8, i1 false)
  %5 = bitcast %struct.test_complex_t* %retval to { double, double }*
  %6 = load { double, double }* %5, align 1
  ret { double, double } %6
}

declare void @llvm.memcpy.p0i8.p0i8.i64(i8* nocapture, i8* nocapture, i64, i32, i1) nounwind

define void @cidentity2_1({ double, double }* sret %oval, double %in_val.coerce0, double %in_val.coerce1) nounwind {
  %1 = call {double, double} @cidentity2(double %in_val.coerce0, double %in_val.coerce1)
  %2 = extractvalue { double, double } %1, 0
  %3 = extractvalue { double, double } %1, 1
  %4 = getelementptr inbounds { double, double }* %oval, i32 0, i32 0
  %5 = getelementptr inbounds { double, double }* %oval, i32 0, i32 1
  store double %2, double* %4
  store double %3, double* %5
  ret void
}

define void @test_fn() nounwind uwtable {
entry:
  %v = alloca { double, double }, align 8
  %coerce = alloca { double, double }, align 8
  %coerce3 = alloca { double, double }, align 8
  %coerce11 = alloca { double, double }, align 8
  %real = getelementptr inbounds { double, double }* %coerce, i32 0, i32 0
  %imag = getelementptr inbounds { double, double }* %coerce, i32 0, i32 1
  store double 4.000000e+00, double* %real
  store double 3.000000e+00, double* %imag
  %0 = getelementptr { double, double }* %coerce, i32 0, i32 0
  %1 = load double* %0, align 1
  %2 = getelementptr { double, double }* %coerce, i32 0, i32 1
  %3 = load double* %2, align 1
  %call = call { double, double } @cidentity(double %1, double %3)
  %4 = extractvalue { double, double } %call, 0
  %5 = extractvalue { double, double } %call, 1
  %real1 = getelementptr inbounds { double, double }* %v, i32 0, i32 0
  %imag2 = getelementptr inbounds { double, double }* %v, i32 0, i32 1
  store double %4, double* %real1
  store double %5, double* %imag2
  %v.realp = getelementptr inbounds { double, double }* %v, i32 0, i32 0
  %v.real = load double* %v.realp
  %v.imagp = getelementptr inbounds { double, double }* %v, i32 0, i32 1
  %v.imag = load double* %v.imagp
  %real4 = getelementptr inbounds { double, double }* %coerce3, i32 0, i32 0
  %imag5 = getelementptr inbounds { double, double }* %coerce3, i32 0, i32 1
  store double %v.real, double* %real4
  store double %v.imag, double* %imag5
  %6 = getelementptr { double, double }* %coerce3, i32 0, i32 0
  %7 = load double* %6, align 1
  %8 = getelementptr { double, double }* %coerce3, i32 0, i32 1
  %9 = load double* %8, align 1
  %call6 = call double @creal(double %7, double %9) nounwind
  %v.realp7 = getelementptr inbounds { double, double }* %v, i32 0, i32 0
  %v.real8 = load double* %v.realp7
  %v.imagp9 = getelementptr inbounds { double, double }* %v, i32 0, i32 1
  %v.imag10 = load double* %v.imagp9
  %real12 = getelementptr inbounds { double, double }* %coerce11, i32 0, i32 0
  %imag13 = getelementptr inbounds { double, double }* %coerce11, i32 0, i32 1
  store double %v.real8, double* %real12
  store double %v.imag10, double* %imag13
  %10 = getelementptr { double, double }* %coerce11, i32 0, i32 0
  %11 = load double* %10, align 1
  %12 = getelementptr { double, double }* %coerce11, i32 0, i32 1
  %13 = load double* %12, align 1
  %call14 = call double @cimag(double %11, double %13) nounwind
  %call15 = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([22 x i8]* @.str, i32 0, i32 0), double %call6, double %call14)
  ret void
}

declare i32 @printf(i8*, ...)

declare double @creal(double, double) nounwind

declare double @cimag(double, double) nounwind
