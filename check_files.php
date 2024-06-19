<?php
$dir = 'C:\Users\Intel Nuc\Dropbox\360 dropbox\vid'; // Percorso della directory dei video

$newVideos = array();

if (is_dir($dir)) {
    if ($dh = opendir($dir)) {
        while (($file = readdir($dh)) !== false) {
            $filePath = $dir . '/' . $file;
            if (is_file($filePath)) {
                // Verifica che il file sia un video
                $extension = pathinfo($filePath, PATHINFO_EXTENSION);
                if ($extension === 'mp4' || $extension === 'webm') {
                    $newVideos[] = $file;
                }
            }
        }
        closedir($dh);
    }
}

header('Content-Type: application/json');
echo json_encode($newVideos);
?>
