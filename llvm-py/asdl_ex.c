/* ______________________________________________________________________
   asdl_ex.c

   Sample input to clang to look at how it implements union types in LLVM.

   Adapted version of example in ASDL paper (Wang et al., 1997)
   ______________________________________________________________________ */

#include <stdlib.h>

typedef struct _stm * stm_ty;
typedef struct _exp * exp_ty;

struct _stm {
  enum {
    Compound_kind = 1,
    Assign_kind = 2,
    Print_kind = 3,
  } kind;

  union {
    struct {
      stm_ty stm1;
      stm_ty stm2;
    } Compound;
    struct {
      char * id;
      exp_ty exp;
      exp_ty * exp_opt;
    } Assign;
    struct {
      exp_ty * exps;
    } Print;
  } value;
};

/* ______________________________________________________________________
   Interesting to note that clang will only generate enough type
   declarations to cover the code generated, so I had to define
   constructors for all three kinds.

   Given the types defined above (with the constructors defined below)
   clang generated the following LLVM:

   %struct._stm = type { i32, %union.anon }
   %union.anon = type { %struct.anon.0 }
   %struct.anon.0 = type { i8*, %struct._exp*, %struct._exp** }
   %struct._exp = type opaque
   %struct.anon = type { %struct._stm*, %struct._stm* }
   %struct.anon.1 = type { %struct._exp** }

   So it appears that unions are implemented in LLVM as structures
   that contain the structure of maximum size.  This makes sense since
   the union type will have enough space to hold all possible union
   members.  When accessing a union member, clang gets a pointer to
   the memory holding the union and then bitcasts it to a pointer to
   the proper structure.  Example:

   rv->value.Compound.stm1 = stm1;

   Becomes:

   %7 = load %struct._stm** %1, align 4
   %8 = load %struct._stm** %rv, align 4
   %9 = getelementptr inbounds %struct._stm* %8, i32 0, i32 1
   %10 = bitcast %union.anon* %9 to %struct.anon*
   %11 = getelementptr inbounds %struct.anon* %10, i32 0, i32 0
   store %struct._stm* %7, %struct._stm** %11, align 4

   ______________________________________________________________________ */

stm_ty Compound (stm_ty stm1, stm_ty stm2)
{
  stm_ty rv = (stm_ty)NULL;
  rv = (stm_ty)malloc(sizeof(*rv));
  rv->kind = Compound_kind;
  rv->value.Compound.stm1 = stm1;
  rv->value.Compound.stm2 = stm2;
  return rv;
}

stm_ty Assign (char * id, exp_ty exp, exp_ty * exp_opt)
{
  stm_ty rv = (stm_ty)NULL;
  rv = (stm_ty)malloc(sizeof(*rv));
  rv->kind = Assign_kind;
  rv->value.Assign.id = id;
  rv->value.Assign.exp = exp;
  rv->value.Assign.exp_opt = exp_opt;
  return rv;
}

stm_ty Print (exp_ty * exps)
{
  stm_ty rv = (stm_ty)NULL;
  rv = (stm_ty)malloc(sizeof(*rv));
  rv->kind = Print_kind;
  rv->value.Print.exps = exps;
  return rv;
}

/* ______________________________________________________________________
   End of asdl_ex.c
   ______________________________________________________________________ */
