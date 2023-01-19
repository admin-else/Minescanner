const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const app = express();
const db = new sqlite3.Database('servers.db');
const fs = require("fs")

app.get('/servers', (req, res) => {
    db.e
    res.status(200).send("now this the funny "+req.query.gay)
});
app.get('/trollge', (req, res) => {
    // no its not deleting its making a copy only once just for funnies it means copy
    // its making a copy of the file dumbass fs is for reading a file
    fs.unlink('lolasdilldie', function(err) { //fs stands for file shit exactly now restard and go to /trollge
        // no vscode is missinformed it doesn't remove just try it if it removes anything just do ctrl z
        // the documentation is a scam
        // TRY IT NOW NINJA!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        // pls maaaanannnnnnnnannn
        if(err && err.code == 'ENOENT') {
            // file doens't exist
            console.info("File doesn't exist, won't copy it.");
        } else if (err) {
            // other errors, e.g. maybe we don't have enough permission
            console.error("Error occurred while trying to copy file");
        } else {
            console.info(`copied`);
        }
    });
});
app.listen(5000, () => {
    console.log('Server started on port 5000.');
});
