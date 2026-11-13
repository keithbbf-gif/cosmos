<?php
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
$path = '/home/papafigc/lmn_match.json';
$raw = file_get_contents('php://input');
if ($raw === false || strlen($raw) > 12000) {
    http_response_code(400);
    echo '{"error":"bad"}';
    exit;
}
$in = json_decode($raw, true);
if (!is_array($in)) {
    http_response_code(400);
    echo '{"error":"bad"}';
    exit;
}
$op = isset($in['op']) ? $in['op'] : '';
$pid = isset($in['pid']) ? preg_replace('/[^a-zA-Z0-9_-]/', '', substr((string) $in['pid'], 0, 40)) : '';
if ($pid === '') {
    http_response_code(400);
    echo '{"error":"pid"}';
    exit;
}
$fp = fopen($path, 'c+');
if (!$fp) {
    http_response_code(500);
    echo '{"error":"store"}';
    exit;
}
flock($fp, LOCK_EX);
$state = json_decode(stream_get_contents($fp) ?: '', true);
if (!is_array($state)) {
    $state = array('queue' => array(), 'matches' => array());
}
$now = time();
$games = array('higher' => 1, 'tiles' => 1, 'derby' => 1);
if (isset($in['game']) && preg_match('/^[sm][0-9]{2}$/', (string) $in['game'])) {
    $games[(string) $in['game']] = 1;
}
$modes = array('human' => 1, 'ai' => 1, 'either' => 1);

function out_json($fp, $state, $payload) {
    ftruncate($fp, 0);
    rewind($fp);
    fwrite($fp, json_encode($state));
    fflush($fp);
    flock($fp, LOCK_UN);
    fclose($fp);
    echo json_encode($payload);
    exit;
}

function clean_name($name) {
    $name = preg_replace('/[^a-zA-Z0-9 _-]/', '', substr((string) $name, 0, 16));
    return $name === '' ? 'Player' : $name;
}

function public_match($match, $pid) {
    if (empty($match['roster']) || !is_array($match['roster'])) {
        return array('id' => $match['id'], 'game' => $match['game'], 'seed' => isset($match['seed']) ? $match['seed'] : 1, 'seats' => array(), 'moves' => new stdClass(), 'you' => $pid);
    }
    $roster = $match['roster'];
    $slot = 'a1';
    foreach ($roster as $s) {
        if (!empty($s['pid']) && $s['pid'] === $pid) {
            $slot = $s['slot'];
        }
    }
    $side = $slot[0];
    $other = $side === 'a' ? 'b' : 'a';
    $mate = $side . ($slot[1] === '1' ? '2' : '1');
    $map = array('you' => $slot, 'teammate' => $mate, 'enemy' => $other . '1', 'enemy2' => $other . '2');
    $by = array();
    foreach ($roster as $s) {
        $by[$s['slot']] = $s;
    }
    $seats = array();
    foreach ($map as $role => $sl) {
        $s = $by[$sl];
        $seats[] = array('role' => $role, 'kind' => $s['kind'], 'name' => $s['name'], 'pid' => $s['pid'], 'skill' => $s['skill']);
    }
    $moves = isset($match['moves']) && is_array($match['moves']) && count($match['moves']) ? $match['moves'] : new stdClass();
    return array('id' => $match['id'], 'game' => $match['game'], 'seed' => $match['seed'], 'seats' => $seats, 'moves' => $moves, 'you' => $pid);
}

function slot_row($slot, $kind, $name, $pid, $skill) {
    return array('slot' => $slot, 'kind' => $kind, 'name' => $name, 'pid' => $pid, 'skill' => $skill);
}

function ai_seat($role, $name, $skill) {
    return array('role' => $role, 'kind' => 'ai', 'name' => $name, 'pid' => '', 'skill' => $skill);
}

function human_seat($role, $ticket) {
    return array('role' => $role, 'kind' => 'human', 'name' => $ticket['name'], 'pid' => $ticket['pid'], 'skill' => 0);
}

$state['queue'] = array_values(array_filter($state['queue'], function ($q) use ($now) {
    return isset($q['seen']) && ($now - (int) $q['seen']) < 45;
}));
$state['matches'] = array_values(array_filter($state['matches'], function ($m) use ($now) {
    return isset($m['created']) && ($now - (int) $m['created']) < 1200;
}));

function find_ticket(&$queue, $pid) {
    foreach ($queue as $i => $q) {
        if ($q['pid'] === $pid) {
            return $i;
        }
    }
    return -1;
}

function drop_pids(&$queue, $pids) {
    $queue = array_values(array_filter($queue, function ($q) use ($pids) {
        return !in_array($q['pid'], $pids, true);
    }));
}

function try_make(&$state, $now) {
    $by = array();
    foreach ($state['queue'] as $q) {
        $by[$q['game']][] = $q;
    }
    foreach ($by as $game => $tickets) {
        $used = array();
        $n = count($tickets);
        for ($i = 0; $i < $n; $i++) {
            $a = $tickets[$i];
            if (isset($used[$a['pid']])) {
                continue;
            }
            $age = $now - (int) $a['since'];
            $enemy = null;
            $mate = null;
            $needEnemy = $a['enemy'] !== 'ai';
            $needMate = $a['teammate'] !== 'ai';
            if ($needEnemy) {
                for ($j = 0; $j < $n; $j++) {
                    $b = $tickets[$j];
                    if ($b['pid'] === $a['pid'] || isset($used[$b['pid']])) {
                        continue;
                    }
                    if ($b['enemy'] === 'ai') {
                        continue;
                    }
                    $enemy = $b;
                    break;
                }
            }
            if ($needMate) {
                for ($j = 0; $j < $n; $j++) {
                    $c = $tickets[$j];
                    if ($c['pid'] === $a['pid'] || isset($used[$c['pid']])) {
                        continue;
                    }
                    if ($enemy && $c['pid'] === $enemy['pid']) {
                        continue;
                    }
                    if ($c['teammate'] === 'ai') {
                        continue;
                    }
                    $mate = $c;
                    break;
                }
            }
            $enemyReady = !$needEnemy || $enemy || ($a['enemy'] === 'either' && ($age >= 8 || $mate));
            $mateReady = !$needMate || $mate || ($a['teammate'] === 'either' && ($age >= 8 || $enemy));
            if (!$enemyReady || !$mateReady) {
                continue;
            }
            $roster = array(
                slot_row('a1', 'human', $a['name'], $a['pid'], 0),
                $mate ? slot_row('a2', 'human', $mate['name'], $mate['pid'], 0) : slot_row('a2', 'ai', 'Librarian', '', 0.76),
                $enemy ? slot_row('b1', 'human', $enemy['name'], $enemy['pid'], 0) : slot_row('b1', 'ai', 'Sprinter', '', 0.58),
                slot_row('b2', 'ai', 'Novelist', '', 0.4),
            );
            $pids = array($a['pid']);
            if ($mate) {
                $pids[] = $mate['pid'];
            }
            if ($enemy) {
                $pids[] = $enemy['pid'];
            }
            $match = array(
                'id' => 'm' . $now . substr(md5($a['pid'] . $game), 0, 6),
                'game' => $game,
                'seed' => $now % 100000 + mt_rand(1, 999),
                'roster' => $roster,
                'moves' => array(),
                'created' => $now,
                'pids' => $pids,
            );
            foreach ($pids as $p) {
                $used[$p] = 1;
            }
            drop_pids($state['queue'], $pids);
            $state['matches'][] = $match;
            return $match;
        }
    }
    return null;
}

if ($op === 'save') {
    $rec = isset($in['record']) && is_array($in['record']) ? $in['record'] : null;
    $allow = array('game', 'event', 'match_id', 'seed', 'models', 'calls', 'lanes', 'seats', 'outcome');
    $keep = array('ts' => gmdate('c'));
    if ($rec) {
        foreach ($allow as $key) {
            if (array_key_exists($key, $rec)) {
                $keep[$key] = $rec[$key];
            }
        }
    }
    $line = json_encode($keep);
    if (!is_array($rec) || $line === false || strlen($line) > 24000) {
        out_json($fp, $state, array('error' => 'record'));
    }
    $log = '/home/papafigc/lmn_runs.jsonl';
    file_put_contents($log, $line . "\n", FILE_APPEND | LOCK_EX);
    out_json($fp, $state, array('status' => 'saved'));
}

if ($op === 'join') {
    $game = isset($in['game']) ? $in['game'] : '';
    $tm = isset($in['teammate']) ? $in['teammate'] : 'ai';
    $en = isset($in['enemy']) ? $in['enemy'] : 'ai';
    if (!isset($games[$game]) || !isset($modes[$tm]) || !isset($modes[$en])) {
        out_json($fp, $state, array('error' => 'mode'));
    }
    $name = clean_name(isset($in['name']) ? $in['name'] : '');
    $state['queue'] = array_values(array_filter($state['queue'], function ($q) use ($pid) {
        return $q['pid'] !== $pid;
    }));
    $ticket = array(
        'pid' => $pid,
        'name' => $name,
        'game' => $game,
        'teammate' => $tm,
        'enemy' => $en,
        'since' => $now,
        'seen' => $now,
    );
    if ($tm === 'ai' && $en === 'ai') {
        $match = array(
            'id' => 'm' . $now . substr(md5($pid), 0, 6),
            'game' => $game,
            'seed' => $now % 100000 + mt_rand(1, 999),
            'roster' => array(
                slot_row('a1', 'human', $name, $pid, 0),
                slot_row('a2', 'ai', 'Librarian', '', 0.76),
                slot_row('b1', 'ai', 'Sprinter', '', 0.58),
                slot_row('b2', 'ai', 'Novelist', '', 0.4),
            ),
            'moves' => array(),
            'created' => $now,
            'pids' => array($pid),
        );
        $state['matches'][] = $match;
        out_json($fp, $state, array('status' => 'matched', 'match' => public_match($match, $pid)));
    }
    $state['queue'][] = $ticket;
    $made = try_make($state, $now);
    $idx = find_ticket($state['queue'], $pid);
    if ($idx >= 0) {
        out_json($fp, $state, array('status' => 'queued', 'wait' => $now - $ticket['since']));
    }
    foreach ($state['matches'] as $m) {
        if (in_array($pid, $m['pids'], true) && $m['created'] === $now) {
            out_json($fp, $state, array('status' => 'matched', 'match' => public_match($m, $pid)));
        }
    }
    if ($made && in_array($pid, $made['pids'], true)) {
        out_json($fp, $state, array('status' => 'matched', 'match' => public_match($made, $pid)));
    }
    out_json($fp, $state, array('status' => 'queued', 'wait' => 0));
}

if ($op === 'poll') {
    foreach ($state['queue'] as $i => $q) {
        if ($q['pid'] === $pid) {
            $state['queue'][$i]['seen'] = $now;
        }
    }
    $made = try_make($state, $now);
    foreach ($state['matches'] as $m) {
        if (in_array($pid, $m['pids'], true)) {
            out_json($fp, $state, array('status' => 'matched', 'match' => public_match($m, $pid)));
        }
    }
    $wait = 0;
    foreach ($state['queue'] as $q) {
        if ($q['pid'] === $pid) {
            $wait = $now - (int) $q['since'];
        }
    }
    out_json($fp, $state, array('status' => 'queued', 'wait' => $wait, 'queued' => count($state['queue'])));
}

if ($op === 'move') {
    $mid = isset($in['match']) ? preg_replace('/[^a-zA-Z0-9]/', '', substr((string) $in['match'], 0, 24)) : '';
    $round = isset($in['round']) ? (string) intval($in['round']) : '0';
    $pick = isset($in['pick']) ? substr((string) $in['pick'], 0, 80) : '';
    foreach ($state['matches'] as $i => $m) {
        if ($m['id'] !== $mid || !in_array($pid, $m['pids'], true)) {
            continue;
        }
        if (!isset($state['matches'][$i]['moves'][$round]) || !is_array($state['matches'][$i]['moves'][$round])) {
            $state['matches'][$i]['moves'][$round] = array();
        }
        $state['matches'][$i]['moves'][$round][$pid] = $pick;
        out_json($fp, $state, array('status' => 'ok', 'match' => public_match($state['matches'][$i], $pid)));
    }
    out_json($fp, $state, array('error' => 'nomatch'));
}

if ($op === 'leave') {
    $state['queue'] = array_values(array_filter($state['queue'], function ($q) use ($pid) {
        return $q['pid'] !== $pid;
    }));
    out_json($fp, $state, array('status' => 'left'));
}

out_json($fp, $state, array('error' => 'op'));
