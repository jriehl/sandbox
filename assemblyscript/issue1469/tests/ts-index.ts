/**
 * Run me:
 * % npx tsc -b && node ts-index
 */

import * as assert from 'assert';
import * as assembly from '../assembly';

{
    const adder = assembly.Adders.buildPrefixIntegerAdder();
    const tree = assembly.Tree.buildATree();
    const result = adder.visitPrefix(tree);
    assert.strictEqual(result, 6);
}

console.log('ok');