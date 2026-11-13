<?php
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
$path = '/home/papafigc/lmn_runs.jsonl';
$runs = array();
if (is_file($path)) {
    $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    if (is_array($lines)) {
        foreach ($lines as $line) {
            $row = json_decode($line, true);
            if (is_array($row)) {
                $runs[] = $row;
            }
        }
    }
}
echo json_encode(array('count' => count($runs), 'runs' => $runs));
