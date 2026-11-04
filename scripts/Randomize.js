// Shared by the QML renderer and the Node regression suite.
function shuffled(values, random) {
    var result = values.slice();
    for (var i = result.length - 1; i > 0; --i) {
        var j = Math.floor(random() * (i + 1));
        var temp = result[i]; result[i] = result[j]; result[j] = temp;
    }
    return result;
}

function assign(names, files, previous, random) {
    random = random || Math.random;
    var result = {};
    if (!files.length) return result;
    // Randomized matching avoids duplicates AND unchanged displays whenever
    // possible; greedy selection can strand the last screen with its old image.
    var slots = [];
    while (slots.length < names.length) slots = slots.concat(shuffled(files, random));
    var owners = {};
    function match(screen, seen, avoidPrevious) {
        var order = shuffled(slots.map(function(_, i) { return i; }), random);
        for (var k = 0; k < order.length; ++k) {
            var i = order[k];
            if (seen[i] || (avoidPrevious && slots[i] === previous[names[screen]])) continue;
            seen[i] = true;
            if (owners[i] === undefined || match(owners[i], seen, avoidPrevious)) {
                owners[i] = screen;
                return true;
            }
        }
        return false;
    }
    // With enough images, expose exactly one slot per file.
    if (files.length >= names.length) slots = shuffled(files, random);
    for (var n = 0; n < names.length; ++n) {
        if (!match(n, {}, true)) match(n, {}, false);
    }
    Object.keys(owners).forEach(function(i) { result[names[owners[i]]] = slots[i]; });
    return result;
}
