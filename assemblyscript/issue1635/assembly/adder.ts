import { Tree } from './tree';

export namespace Adders {
    export abstract class Adder<T, U> {
        constructor(
            public zero: U
        ) {}

        public abstract add(arg0: T, arg1: T): U;
    }

    export class PrefixAdder<T> extends Tree.TreeVisitor<T, T> {
        constructor(
            public adder: Adder<T, T>
        ) {
            super();
        }

        visitPrefix(node: Tree.Node<T> | null): T {
            if (node == null) {
                return this.adder.zero;
            } else {
                return this.adder.add(
                    this.adder.add(node.payload, this.visitPrefix(node.left)),
                    this.visitPrefix(node.right)
                );
            }
        }
    }

    export class IntegerAdder extends Adder<i32, i32> {
        constructor() {
            super(0);
        }

        add(arg0: i32, arg1: i32): i32 {
            return arg0 + arg1;
        }
    }

    export class PrefixIntegerAdder extends PrefixAdder<i32> {
    }

    export function buildPrefixIntegerAdder(): PrefixIntegerAdder {
        return new PrefixIntegerAdder(new IntegerAdder());
    }
}
