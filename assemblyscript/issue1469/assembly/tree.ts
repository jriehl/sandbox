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

    export interface TreeVisitor<T, U> {
        visitPrefix(node: Node<T> | null): U;
    }
}
