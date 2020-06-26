<?php
/* TITLE: IPP (test.php)
    - Author: Maros Geffert
    - Login: <xgeffe00>
*/

$iCheckArguments = new Arguments();
$iCheckArguments->iCheckArgs();

// Shortcuts
$iR = $iCheckArguments->iRecursive;
$iP = $iCheckArguments->iParsePath;
$iI = $iCheckArguments->iInterpretPath;
$iIO = $iCheckArguments->iIntOnly;
$iPO = $iCheckArguments->iParseOnly;
$iJ = $iCheckArguments->iJexamXml;
$iX = $iCheckArguments->iXmlOptionsPath;

$iFileScanner = new iFileScanner($iR, $iP, $iI, $iIO, $iPO, $iJ, $iX);
$iFileScanner->Scanner($iCheckArguments->iActualDir);


class Arguments {

    public function  __construct()
    {
        // Define default cwd
        $this->iActualDir = "./tests/";
        //$this->iActualDir = getcwd()."/tests/";
        $this->iParsePath = "./parse.php";
        $this->iInterpretPath = "./interpret.py";
        $this->iJexamXml = "./pub/courses/ipp/jexamxml/jexamxml.jar";
        $this->iXmlOptionsPath = "./jexamxml/options";

        $this->iRecursive = false;
        $this->iParseOnly = false;
        $this->iIntOnly = false;
    }

    public function iCheckArgs() {
        // Process arguments
        global $argc;
        $options = array("help", "directory:", "recursive", "parse-script:", "int-script:", "parse-only", "int-only", "jexamxml:");
        $options = getopt(null, $options);

        if(isset($options['help']) and $argc == 2) {
            printf("--- HELP ---");
            printf("Script for testing IPP project -> interpret and parse");
            printf("Script work with some important arguments ->");
            printf("\"help\", \"directory:\", \"recursive\", \"parse-script:\", \"int-script:\", \"parse-only\", \"int-only\", \"jexamxml\"");
            printf("All scripts result are printed in HTML file");
            exit(10);
        }

        if(isset($options['parse-script'])) {
            $this->iParsePath = $options['parse-script'];
            if (!file_exists($this->iParsePath)) {
                fprintf(STDERR, "ERROR: File does not exist".$this->iParsePath);
                exit(10);
            }
        }

        if(isset($options['int-script'])) {
            $this->iInterpretPath = $options['int-script'];
            if (!file_exists($this->iInterpretPath)) {
                fprintf(STDERR, "ERROR: File does not exist" . $this->iInterpretPath);
                exit(10);
            }
        }

        if(isset($options['parse-only'])) {
            if(isset($options['int-only']) or isset($options['int-script'])) {
                fprintf(STDERR, "ERROR: You cannot combine Parse mode with Int mode !");
                exit(11);
            }
            $this->iParseOnly = true;
        }

        if(isset($options['int-only'])) {
            if(isset($options['parse-only']) or isset($options['parse-script'])) {
                fprintf(STDERR, "ERROR: You cannot combine Parse mode with Int mode !");
                exit(11);
            }
            $this->iIntOnly = true;
        }

        if(isset($options['jexamxml'])) {
            $this->iJexamXml = $options['jexamxml'];
            $this->iXmlOptionsPath = $options['jexamxml']."/options";
            if (!file_exists($this->iJexamXml)) {
                fprintf(STDERR, "ERROR: File does not exist" . $this->iJexamXml);
                exit(10);
            }
        }

        if(array_key_exists('directory', $options)) {
            if(is_dir($options['directory'])) {
                $this->iActualDir = $options['directory'];
            }
            else {
                fprintf(STDERR, "Directory does not exist -> ".$options['directory']);
                exit(11);
            }
            if (substr($options['directory'], -1) != '/') {
                $this->iActualDir = $options['directory']."/";
            }
        }

        if(array_key_exists('recursive', $options)) {
            $this->iRecursive = true;
        }
    }
}

class iFileScanner {

    private $iFolders;
    private $iResults;

    public function  __construct($iRecursive, $iParsePath, $iInterpretPath,  $iIntOnly, $iParseOnly, $iJexamXml, $iXmlOptionsPath)
    {
        $this->iFolders = array();
        $this->iResults = array();
        $this->iRecursive = $iRecursive;
        $this->iParsePath = $iParsePath;
        $this->iInterpretPath = $iInterpretPath;
        $this->iParseOnly = $iParseOnly;
        $this->iIntOnly = $iIntOnly;
        $this->iJexamlXml = $iJexamXml;
        $this->iXmlOptions = $iXmlOptionsPath;
        $this->iParseOrInt = $this->ParseOrInt();
    }

    // Proccess, which mode is choosen, (parse,int or both only)
    public function ParseOrInt() {
        if ($this->iParseOnly == true)
            $iParseOrInt = 'Parse';
        else if ($this->iIntOnly == true)
            $iParseOrInt = 'Int';
        else
            $iParseOrInt = '-';
        return $iParseOrInt;
    }

    public function Scanner($iDir) {
        if(!file_exists(($iDir)))
            return;

        // Dictionary, where i store information about file
        $iNumber_of_folder = count($this->iFolders);
        $this->iFolders[$iNumber_of_folder]["name"] = $iDir;
        $this->iFolders[$iNumber_of_folder]["good"] = 0;
        $this->iFolders[$iNumber_of_folder]["bad"] = 0;
        $this->iFolders[$iNumber_of_folder]["total"] = 0;
        $this->iFolders[$iNumber_of_folder]["percentage"] = 0;

        $iFileArray = scandir($iDir);
        $iCountOfFiles = 0;

        // Find or generate files
        foreach($iFileArray as $iFile) {
            if(is_dir($iDir.$iFile)) {
                if($this->iRecursive == true) {
                    if ($iFile == "." || $iFile == "..")
                        unset($iFileArray[$iCountOfFiles]);
                    else {
                        $this->Scanner($iDir.$iFile."/");
                    }

                }
            }
            else {
                if (preg_match("/.src$/", $iFile)) {
                    $srcFile = $iFile;
                    $iBase = substr($iFile, 0, -3);
                    if (!file_exists($iDir . $iBase . "in")) {
                        $inFile = $this->iGenerateFile($iDir . $iBase . 'in', "");
                    } else {
                        $inFile = $iDir . $iBase . "in";
                    }
                    if (!file_exists($iDir . $iBase . "out")) {
                        $outFile = $this->iGenerateFile($iDir . $iBase . 'out', "");
                    } else {
                        $outFile = $iDir . $iBase . "out";
                    }
                    if (!file_exists($iDir . $iBase . "rc")) {
                        $rcFile = $this->iGenerateFile($iDir . $iBase . 'rc', "0");
                    } else {
                        $rcFile = $iDir . $iBase . "rc";
                    }
                } else {
                    continue;
                }

                $iBaseWithoutDot = substr($iBase, 0, -1);
                $path = $iDir . $iBaseWithoutDot;

                // Process Both
                if ($this->iParseOnly == false and $this->iIntOnly == false) {
                   $this->iBoth($rcFile, $srcFile, $outFile, $path, $iNumber_of_folder);
                }
                // Process parse only
                else if ($this->iParseOnly == true) {
                    $this->iParseOnly($rcFile, $srcFile, $path, $iNumber_of_folder);
                }
                // Process int only
                else if ($this->iIntOnly == true) {
                    $this->iIntOnly($rcFile, $srcFile, $path, $iNumber_of_folder);
                }
            }
            $iCountOfFiles++;
        }
    }

    // -----------------------------------------------------------------------------------------------------------------

    public function iBoth($rcFile, $srcFile, $outFile, $path, $iNumber_of_folder) {
            exec("php7.4 " . $this->iParsePath . " <\"$path.src\" >\"$path.tmp.in\"", $iOutPut, $iReturnVar);
            $xml_rc_val = $iReturnVar;

            // Compare if output value of xml is 0
            if ($xml_rc_val == 0) {
                $xml_rc = 'true';
            }
            else {
                $xml_rc = 'false';
            }

            exec("python3.8 " . $this->iInterpretPath . " --source=\"$path.tmp.in\" --input=\"$path.in\" >\"$path.tmp.out\"", $iOutPut, $iReturnVar);
            $int_rc_value = file_get_contents($rcFile);
            $both_mvalue = $iReturnVar;

            // Compare if python interpret value is right
            if ($int_rc_value == $both_mvalue) {
                $int_rc = 'true';
            } else {
                $int_rc = 'false';
            }

            //exec("printf $iReturnVar | diff -q - \"$rcFile\"", $iOutPut, $iReturnVar);
            exec("diff -q \"$path.out\" \"$path.tmp.out\"", $iOutPut, $iReturnVar);
            $both_output = file_get_contents($outFile);
            $both_moutput = file_get_contents($path.'.tmp.out');

            // Compare output files interpret and reference output
            if ($both_moutput == 0 or $both_output == $both_moutput) {
                $int_output = 'true';
            } else {
                $int_output = 'false';
            }

            unlink("$path.tmp.out");
            unlink("$path.tmp.in");

            if ($xml_rc == 'true' and $int_rc == 'true' and $int_output == 'true') {
                $FINAL = 'true';
            } else {
                $FINAL = 'false';
            }

            $parse_value = '-';
            $parse_final = '-';
            $int_final = '-';
            $parse_out = '-';

            $this->iResults[$iNumber_of_folder][] = array($srcFile, $parse_out, $xml_rc_val, $parse_value, $parse_final, $int_output, $both_mvalue, $int_rc_value, $int_final, $FINAL);

            if ($FINAL == 'true') {
                $this->iFolders[$iNumber_of_folder]['good']++;
            } else {
                $this->iFolders[$iNumber_of_folder]['bad']++;
            }
            $this->iFolders[$iNumber_of_folder]['total']++;
            $this->iFolders[$iNumber_of_folder]['percentage'] = $this->iFolders[$iNumber_of_folder]['good'] / $this->iFolders[$iNumber_of_folder]['total'] * 100;
    }

    // -----------------------------------------------------------------------------------------------------------------

    public function iParseOnly($rcFile, $srcFile, $path, $iNumber_of_folder) {
        exec("php " . $this->iParsePath . " <\"$path.src\" >\"$path.tmp.in\"", $iOutPut, $iReturnVar);
        $parse_value = file_get_contents($rcFile);
        $parse_mvalue = $iReturnVar;

        if($parse_value != 0) {
            $Error_input = true;
        }
        else {
            $Error_input = false;
        }

        exec( "java -jar \"$this->iJexamlXml\" \"$path.out\" \"$path.tmp.in\"", $iOutPut, $iReturnVar);

        // Compare if XML output is == with reference output (JEXAM)
        if ($iReturnVar == 0) {
            $parse_out = 'true';
        } else {
            if($Error_input == true and $parse_value == $parse_mvalue) {
                $parse_out = 'true';
            }
            else {
                $parse_out = 'false';
            }
        }

        if ($parse_out == 'true' and $parse_value == $parse_mvalue) {
            $parse_final = 'true';
        } else {
            $parse_final = 'false';
        }

        unlink("$path.tmp.in");

        $int_out = '-';
        $int_mvaule = '-';
        $int_value = '-';
        $int_final = '-';
        $FINAL = '-';

        $this->iResults[$iNumber_of_folder][] = array($srcFile, $parse_out, $parse_mvalue, $parse_value, $parse_final, $int_out, $int_mvaule, $int_value, $int_final, $FINAL);

        if ($parse_final == 'true') {
            $this->iFolders[$iNumber_of_folder]['good']++;
        } else {
            $this->iFolders[$iNumber_of_folder]['bad']++;
        }
        $this->iFolders[$iNumber_of_folder]['total']++;
        $this->iFolders[$iNumber_of_folder]['percentage'] = $this->iFolders[$iNumber_of_folder]['good'] / $this->iFolders[$iNumber_of_folder]['total'] * 100;
    }

    // -----------------------------------------------------------------------------------------------------------------

    public function iIntOnly($rcFile, $srcFile, $path, $iNumber_of_folder) {
        exec("python3.8 " . $this->iInterpretPath . " --source=\"$path.src\" --input=\"$path.in\" >\"$path.tmp.out\"", $iOutPut, $iReturnVar);
        $expected_value = file_get_contents($rcFile);
        $my_value = $iReturnVar;

        // Compare output value with reference output value
        if ($expected_value == $my_value) {
            $rc = 'true';
        } else {
            $rc = 'false';
        }

        exec("diff -q \"$path.out\" \"$path.tmp.out\"", $iOutPut, $iReturnVar);
        $MyOutput = file_get_contents($path.".tmp.out");

        // Compare output with reference output
        if ($iReturnVar == 0) {
            $int_out = 'true';
        } else {
            if($expected_value != 0 and $MyOutput == '') {
                $int_out = 'true';
            }
            else {
                $int_out = 'false';
            }
        }

        if ($rc == 'true' and $int_out == 'true') {
            $int_final = 'true';
        } else {
            $int_final = 'false';
        }

        $parse_out = '-';
        $parse_value = '-';
        $parse_mvalue = '-';
        $FINAL = '-';
        $parse_final = '-';

        unlink("$path.tmp.out");

        $this->iResults[$iNumber_of_folder][] = array($srcFile, $parse_out, $parse_value, $parse_mvalue, $parse_final, $int_out, $my_value, $expected_value, $int_final, $FINAL);

        if ($int_final == 'true') {
            $this->iFolders[$iNumber_of_folder]['good']++;
        } else {
            $this->iFolders[$iNumber_of_folder]['bad']++;
        }
        $this->iFolders[$iNumber_of_folder]['total']++;
        $this->iFolders[$iNumber_of_folder]['percentage'] = $this->iFolders[$iNumber_of_folder]['good'] / $this->iFolders[$iNumber_of_folder]['total'] * 100;
    }

    public function iGenerateFile($path, $content) {
        file_put_contents($path, $content);
        return $path;
    }

    public function isEmptyFolder(){

        $howMany = count($this->iFolders)-1;
        // --- Check if some folder was scanned ---
        if(count($this->iFolders) == 0)
        {
            print("In test folder is $howMany valid folder for printing\n");
            exit(10);
        }
        else if(count($this->iFolders) == 1)
        {
            print("In test folder is $howMany valid folder for printing\n");
        }
        else
        {
            print("In test folder are $howMany valid folders for printing\n");
        }
    }

    public function iHTML() {
        $iFolderCnt = -1;
        foreach($this->iFolders as $iDiretory)
        {
            $iFolderCnt++;
            if(!isset($this->iResults[$iFolderCnt])) {
                continue;
            }
            ?>
            <p>
            <div class="folder">
            <h3>Folder -> <?php echo $iDiretory["name"]; ?></h3>
            <font color = "green"> [Passed: <?php echo $iDiretory['good']."/".$iDiretory['total']; ?>]</font>
            <font color = "red">   [Failed: <?php echo $iDiretory['bad']."/".$iDiretory['total']; ?>]</font>
                           [Total success: <?php echo $iDiretory['percentage']; ?>%]
            <?php
            if(isset($this->iResults[$iFolderCnt])) {
            ?>
            <table>
                <tr>
                    <th> File Name </th>
                    <th> JEXAM-XML </th>
                    <th> My Ret. Code (parse) </th>
                    <th> Expec. Ret. Code (parse)</th>
                    <th> Parse Final </th>
                    <th> Int. Output</th>
                    <th> My. Ret. Code (interpret)</th>
                    <th> Expec. Ret. Code (interpret)</th>
                    <th> Interpret Final</th>
                    <th> BOTH FINAL</th>
                </tr>
                <?php

                foreach($this->iResults[$iFolderCnt] as $iRow) {
                    ?>
                    <tr>
                        <td><?php echo $iRow[0]; ?></td>
                        <td class="result" id="<?php echo $iRow[1]; ?>"> </td>
                        <td> <?php echo $iRow[2]; ?></td>
                        <td> <?php echo $iRow[3]; ?></td>
                        <td class="result" id="<?php echo $iRow[4]; ?>"> </td>
                        <td class="result" id="<?php echo $iRow[5]; ?>"> </td>
                        <td> <?php echo $iRow[6]; ?></td>
                        <td> <?php echo $iRow[7]; ?></td>
                        <td class="result" id="<?php echo $iRow[8]; ?>"> </td>
                        <td class="result" id="<?php echo $iRow[9]; ?>"> </td>
                    </tr>
                    <?php
                }
                ?>
                </table>
            </div>
            </p>
            <?php
        }
        }
    }
}

?>
<!DOCTYPE HTML>
<html lang="cs">
<head>
    <meta charset="utf-8" />
    <style>
        body
        {
            background-color: lightgrey;
            text-align: center;
            margin: 30px;
            font-family: Monaco, serif;
        }

        h1
        {
            font-size: 40px;
            color: white;
        }

        h2
        {
            font-size: 30px;
            color: white;
        }

        .container
        {
            margin: auto;
            width: 80%;
            min-width: 800px;
        }

        .header
        {
            background-color: lightskyblue;
            text-align: center;
            padding: 10px;
        }

        .content
        {
            background-color: white;
            padding: 15px;
        }

        .folder
        {
            background-color: white;
            padding: 15px;
        }

        table, th, tr, td
        {
            padding: 1vh;
        }

        table th
        {
            background-color:  lightblue;
        }

        table tr:nth-child(even)
        {
            background-color: lightskyblue;
        }
        table tr:nth-child(odd)
        {
            background-color: lightblue;
        }

        .result
        {
            width: 50px;
        }

        #true
        {
            background-color: lightgreen;
        }

        #false
        {
            background-color: lightcoral;
        }

        #-
        {
        }

    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1 color="blue">~ IPP 2020, (parse.php, interper.py) results ~</h1>
        <h2><?php if($iFileScanner->iParseOrInt == 'Parse') {
            ?> PARSE-ONLY <?php
            }
            else if ($iFileScanner->iParseOrInt == 'Int') {
                ?> INT-ONLY <?php
            }
            else {
                ?> BOTH <?php
            }?></h2>
    </div>
    <div class="content">
        <?php
        $iFileScanner->iHTML();
        $iFileScanner->isEmptyFolder();
        ?>
    </div>
</div>
</body>

</html>
