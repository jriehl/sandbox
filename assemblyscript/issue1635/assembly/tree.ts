export namespace Tree {
    export class Node<T> {
        constructor(
            public payload: T,
            public left: Node<T> | null,
            public right: Node<T> | null
        ) {}
    }

    export function buildATree(): Node<i32> {
        return new Node<i32>(
            2,
            new Node<i32>(1, null, null),
            new Node<i32>(3, null, null)
        );
    }

    export abstract class TreeVisitor<T, U> {
        public abstract visitPrefix(node: Node<T> | null): U;
    }

    export class VoidVisitor<T> extends TreeVisitor<T, void> {
        constructor(
            public visit: (node: Node<T>) => void
        ) {
            super();
        }

        public visitPrefix(node: Node<T> | null): void {
            if (node != null) {
                this.visit(node);
                this.visitPrefix(node.left);
                this.visitPrefix(node.right);
            }
        }
    }

    class DummyVisitor extends VoidVisitor<i32> {
        constructor() {
            super((node: Node<i32>) => {});
        }
    }
}
