/**
 * (Fail to) Run me:
 * % npm run asbuild && npm test
 */

const assert = require("assert");
const myModule = require("..");

{
    const adderPtr = myModule.Adders.buildPrefixIntegerAdder();
    const adder = myModule.Adders.PrefixIntegerAdder.wrap(adderPtr);
    const treePtr = myModule.Tree.buildATree();
    const result = adder.visitPrefix(treePtr);
    assert.strictEqual(result, 6);
}

console.log("ok");
