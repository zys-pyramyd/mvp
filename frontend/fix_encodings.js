const fs = require('fs');
const path = require('path');

const srcDir = path.join(__dirname, 'src');

function fixFile(filePath) {
    let content = fs.readFileSync(filePath, 'utf8');
    let original = content;

    // Replace specific known placeholders with correct UTF-8 symbols
    content = content.replace(/\?\{/g, '₦{');
    content = content.replace(/\?\$/g, '₦$');

    if (filePath.includes('RequestFeed.js')) {
        content = content.replace(/\? Live Instant Requests/g, '⚡ Live Instant Requests');
        content = content.replace(/\?\? Active Farm Requests/g, '🌾 Active Farm Requests');
    }

    if (filePath.includes('RequestsPage.js')) {
        content = content.replace(/\?\? Standard/g, '🌾 Standard');
        content = content.replace(/\? Instant/g, '⚡ Instant');
    }

    if (filePath.includes('MyRequests.js')) {
        content = content.replace(/\?\? ACTION REQUIRED/g, '⚠️ ACTION REQUIRED');
        content = content.replace(/\? Uploading/g, '⏳ Uploading');
        // `? ${f.name}` -> `✅ ${f.name}`
        content = content.replace(/\? \$\{f.name\}/g, '✅ ${f.name}');
    }

    if (content !== original) {
        fs.writeFileSync(filePath, content, 'utf8');
        console.log('Fixed:', filePath);
    }
}

function traverseDir(dir) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
        const fullPath = path.join(dir, file);
        if (fs.statSync(fullPath).isDirectory()) {
            traverseDir(fullPath);
        } else if (fullPath.endsWith('.js') || fullPath.endsWith('.jsx')) {
            fixFile(fullPath);
        }
    }
}

traverseDir(srcDir);
console.log('Done!');
