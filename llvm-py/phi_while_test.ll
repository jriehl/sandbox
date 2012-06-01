; ModuleID = 'phi_while_test_ll'
; ______________________________________________________________________

define i32 @mandel_1(double %real_coord, double %imag_coord, i32 %max_iters) {
Entry:
  br label %LOOP_18

LOOP_18:                                          ; preds = %IF_FALSE_94, %Entry
  %i18 = phi i32 [0, %Entry], [%i94, %IF_FALSE_94]
  %0 = icmp slt i32 %i18, %max_iters
  br i1 %0, label %CONT_30, label %IF_FALSE_30

CONT_30:                                          ; preds = %LOOP_18
  %1 = fadd double 0.000000e+00, %real_coord
  %2 = fmul double 2.000000e+00, %1
  %3 = fmul double %2, 0.000000e+00
  %4 = fadd double %3, %imag_coord
  %5 = fmul double %1, %1
  %6 = fmul double %4, %4
  %7 = fadd double %5, %6
  %8 = fcmp oge double %7, 4.000000e+00
  br i1 %8, label %CONT_94, label %IF_FALSE_94

IF_FALSE_30:                                      ; preds = %LOOP_18
  ret i32 -1

CONT_94:                                          ; preds = %CONT_30
  ret i32 %i18

IF_FALSE_94:                                      ; preds = %CONT_30
  %i94 = add i32 %i18, 1
  br label %LOOP_18
}

; ______________________________________________________________________
; End of phi_while_test.ll
