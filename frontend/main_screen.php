<?php

$DOMAIN_NAME = "localhost";  
$DATABASE_NAME = "doc_intel";
$USERNAME = "root";     //username of phpmyadmin
$PASSWORD = "";     //password of phpmyadmin

//making connection 
$conn = mysqli_connect("$DOMAIN_NAME", "$USERNAME", "", "$DATABASE_NAME");
if($conn)
{
    //echo "Connection Success\n";
}
else
{
    echo "Connection Failed\n";
}


// if ($_SERVER['REQUEST_METHOD'] === 'POST')
//     {
//         $json = file_get_contents('php://input');
//         $data = json_decode($json, true);
//         $num_url = $data['num_url'];
//         $urls = $data['urls'];
//     }


$uploadDir = '../pdf_database';   // directory where pdfs is stored

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $uploadedFile = $_FILES['pdfFile'];

    // Check if the file is a PDF
    $fileType = pathinfo($uploadedFile['name'], PATHINFO_EXTENSION);
    if (strtolower($fileType) !== 'pdf') {
        echo 'Please upload a PDF file.';
        exit;
    }

   // Move the uploaded file to the destination directory
   $destination = $uploadDir . '/' . $uploadedFile['name']; // Include filename in destination path
   move_uploaded_file($uploadedFile['tmp_name'], $destination); // Use tmp_name for moving the file

   echo 'File uploaded successfully: ' . $destination;
// }

$url = 'pdf_database/'.$uploadedFile['name'];
$url_highlighted = 'highlighted_pdf_database/highlight_'.$uploadedFile['name'];
$flaskUrl_extract_one_pdf = 'http://127.0.0.1:5000/extract_one_pdf';

// if($urls != null)
// {
    $data = array(
        'url' => $url
    );

    // Initialize a new cURL session
    $ch = curl_init($flaskUrl_extract_one_pdf);
    // CURLOPT_RETURNTRANSFER instructing cURL to return the response as a string instead of outputting it directly.
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    // Set the request method to POST
    curl_setopt($ch, CURLOPT_POST, true);
    // Set CURLOPT_POSTFIELDS with encoded data
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));

    // Set the content type to JSON
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
        'Content-Type: application/json')
    );
    // Execute the request and store the response
    $response = curl_exec($ch);
    // Close the cURL session
    curl_close($ch);

    if($response)
    {
        $index_name = mt_rand(10000, 99999);
        $responseArray = json_decode($response, true);
        if($responseArray != null)
        {
           
            $videoID = null;
            $videoTitle = null;
            $videoThumbnail = null;
            $product_description = $responseArray['product_description'];
            $link_to_buy_again = $responseArray['link_to_buyAgain'];
            $name = $responseArray['name'];
            $address = $responseArray['address'];
            $pan = $responseArray['PAN'];
            $total = $responseArray['total'];
            $invoiceNumber = $responseArray['invoice_number'];
            $invoiceDate = $responseArray['invoice_date'];
            $productReviewVideos = $responseArray['product_review_video'];
            foreach ($productReviewVideos as $video) {
                $videoTitle = $video['title'];
                $videoID = $video['videoID'];
                $videoThumbnail = $video['thumbnail'];
            }

            $data = array(
                'videoID' => $videoID,
                'videoTitle' => $videoTitle,
                'videoThumbnail' => $videoThumbnail,
                'product_description' => $product_description,
                'link_to_buy_again' => $link_to_buy_again,
                'name' => $name,
                'address' => $address,
                'pan' => $pan,
                'total' => $total,
                'invoiceNumber' => $invoiceNumber,
                'invoiceDate' => $invoiceDate,
                'pdf_path' => $url_highlighted
            );

            $query_string = http_build_query($data);
            $redirect_url = 'input_data.php?' . $query_string;
            header('Location: ' . $redirect_url);
            exit();

            $sql_query = "INSERT INTO `invoice`(`invoice_number`, `invoice_date`, `pan_number`,`name`,`address`,`product_description`,`total_value`,`purchase_links`,`related_video_id`,`related_video_title`,`related_video_thumbnail`) VALUES (?,?,?,?,?,?,?,?,?,?,?)";
            $stmt = mysqli_prepare($conn, $sql_query);
            mysqli_stmt_bind_param($stmt, "sssssssssss", $invoiceNumber, $invoiceDate, $pan, $name, $address, $product_description, $total, $link_to_buy_again, $videoID, $videoTitle, $videoThumbnail);
            mysqli_stmt_execute($stmt);
            if(mysqli_stmt_errno($stmt)) {
                $error_message = mysqli_stmt_error($stmt);
            }
            mysqli_stmt_close($stmt);

            echo "successfull !";
        }
        else
        {
            echo "Error Decoding json data!";
        }
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InvoiceIQ: Automated Invoice Reading and Query System</title>
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #f0f2f5;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 0;
            padding: 20px;
        }
        header {
            text-align: center;
            margin-bottom: 30px;
        }
        h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 0.2em;
        }
        p {
            color: #666;
            font-size: 1.2em;
            max-width: 800px;
            text-align: center;
            margin: 0 auto 20px auto;
        }
        section {
            background: #fff;
            padding: 20px 30px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            max-width: 800px;
            text-align: center;
            margin-bottom: 30px;
        }
        section h2 {
            color: #333;
            margin-bottom: 10px;
            font-size: 1.8em;
        }
        form {
            background: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 500px;
            text-align: center;
        }
        label {
            display: block;
            margin-bottom: 10px;
            font-size: 1.1em;
            color: #333;
        }
        input[type="file"] {
            display: none;
        }
        input[type="file"] + label {
            background-color: #007bff;
            color: white;
            padding: 12px 20px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        input[type="file"] + label:hover {
            background-color: #0056b3;
        }
        input[type="submit"] {
            background-color: #28a745;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1.1em;
            transition: background-color 0.3s;
        }
        input[type="submit"]:hover {
            background-color: #218838;
        }
        .file-name {
            margin-top: 10px;
            font-size: 0.9em;
            color: #333;
        }
        @media (max-width: 768px) {
            section {
                padding: 15px;
            }
            form {
                padding: 15px;
            }
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body>

<header>
    <h1>InvoiceIQ</h1>
    <p>Automated Invoice Reading and Query System</p>
</header>

<!-- <section>
    <h2>Project Overview</h2>
    <p>
        InvoiceIQ is an advanced system designed to streamline the process of managing invoices. By leveraging the power of the 
        Hugging Face library, InvoiceIQ can efficiently scan and extract essential information from invoices. Additionally, 
        the integration of ElasticSearch enhances the system's search capabilities, allowing for quick and precise data retrieval.
    </p>
</section> -->

<form action="main_screen.php" method="post" enctype="multipart/form-data">
    <h2>Upload Your Invoice</h2>
    <input type="file" name="pdfFile" id="pdfFile" onchange="displayFileName()">
    <label for="pdfFile">Choose a PDF file</label>
    <div class="file-name" id="fileName"></div>
    <input type="submit" value="Upload">
</form>

<script>
    function displayFileName() {
        const input = document.getElementById('pdfFile');
        const fileNameDisplay = document.getElementById('fileName');
        fileNameDisplay.textContent = input.files.length > 0 ? `Selected file: ${input.files[0].name}` : '';
    }
</script>

</body>
</html>
