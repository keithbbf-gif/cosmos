<?php
$root = '/home/papafigc/lmnator.com';
$names = array('arcade.html','arcade.js','engines.js','save.js','buy.js','lobby.js','queue.php','runs.php','sw.js','manifest.webmanifest','favicon.svg','site.css','family.css','board.json','pack-single-a.js','pack-single-b.js','pack-multi-a.js','pack-multi-b.js');
$tmp = tempnam(sys_get_temp_dir(), 'lmn');
$zip = new ZipArchive();
if ($zip->open($tmp, ZipArchive::OVERWRITE) !== true) {
    http_response_code(500);
    echo 'zip';
    exit;
}
foreach ($names as $name) {
    $path = $root . '/' . $name;
    if (is_file($path)) $zip->addFile($path, $name);
}
$zip->close();
header('Content-Type: application/zip');
header('Content-Disposition: attachment; filename="lmnator-arcade.zip"');
header('Content-Length: ' . filesize($tmp));
readfile($tmp);
unlink($tmp);
