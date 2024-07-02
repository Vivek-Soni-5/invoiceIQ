<!DOCTYPE html>
<html>
<head>
    <title>Display PDF and User Input</title>
    <style>
        /* Styling for layout */
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }
        .container {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        .pdf-container {
            width: 50%;
            border: 1px solid #ccc;
            padding: 20px;
        }
        .user-input, .search-container {
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            padding: 20px;
            width: 45%;
            margin: 0 auto;
            margin-bottom: 30px;
        }
        h2 {
            margin-top: 0;
            text-align: center;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"],
        input[type="email"],
        textarea {
            width: 100%;
            padding: 8px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        input[type="submit"], button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        input[type="submit"]:hover, button:hover {
            background-color: #45a049;
        }
        .search-container input[type="text"] {
            width: calc(100% - 50px);
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 1.1em;
            margin-right: 10px;
        }
        .search-results {
            margin-top: 20px;
        }
        .search-results p {
            background-color: #e9ecef;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #ccc;
        }
    </style>
</head>
<body>
            <?php
                $received_data = $_GET;
                // Access received data
                $videoID = $received_data['videoID'];
                $videoTitle = $received_data['videoTitle'];
                $videoThumbnail = $received_data['videoThumbnail'];
                $product_description = $received_data['product_description'];
                $link_to_buy_again = $received_data['link_to_buy_again'];
                $name = $received_data['name'];
                $address = $received_data['address'];
                $pan = $received_data['pan'];
                $total = $received_data['total'];
                $invoiceNumber = $received_data['invoiceNumber'];
                $invoiceDate = $received_data['invoiceDate'];
                $pdf_path = $received_data['pdf_path'];
            ?>
    <div class="container">
        <div class="pdf-container">
            <!-- Displaying PDF file -->
            <?php
            $pdfPath = '../'.$pdf_path; // Replace this with your PDF file path
            if (file_exists($pdfPath)) {
                echo '<embed src="' . $pdfPath . '" width="100%" height="800px" />';
            } else {
                echo 'PDF file not found.';
            }
            ?>
        </div>
        <div>
        </div>
        <div class="user-input">
            <!-- Form for user input -->
             
            <h2>AI Generated Data from Invoice</h2>
            <form action="process_input.php" method="post">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <div style="margin-right: 10px;">
                        <label for="invoiceNumber">Invoice Number:</label>
                        <input type="text" id="invoiceNumber" name="invoiceNumber" value="<?php echo isset($invoiceNumber) ? $invoiceNumber : ''; ?>" required>
                    </div>
                    <div style="margin-right: 10px;">
                        <label for="invoiceDate">Invoice Date:</label>
                        <input type="text" id="invoiceDate" name="invoiceDate" value="<?php echo isset($invoiceDate) ? $invoiceDate : ''; ?>" required>
                    </div>
                    <div style="margin-right: 10px;">
                        <label for="name">PAN:</label>
                        <input type="text" id="pan" name="pan" value="<?php echo isset($pan) ? $pan : ''; ?>" required><br>
                    </div> 
                    <div>
                        <label for="name">Total Value:</label>
                        <input type="text" id="total_value" name="total_value" value="<?php echo isset($total) ? $total : ''; ?>" required><br>
                    </div> 
                </div>
                <label for="name">Name:</label>
                <input type="text" id="name" name="name" value="<?php echo isset($name) ? $name : ''; ?>" required><br>
                <label for="name">Address:</label>
                <input type="text" id="address" name="address" value="<?php echo isset($address) ? $address : ''; ?>" required><br>
                
                <label for="name">Link to purchase:</label>
                <input type="text" id="link_to_purchase_again" name="link_to_purchase_again" value="<?php echo isset($link_to_buy_again) ? $link_to_buy_again : ''; ?>" required><br>
                <label for="name">Product Description:</label>
                <input type="text" id="product_description" name="product_description" rows="4" cols="30" value="<?php echo isset($product_description) ? $product_description : ''; ?>" required><br>
                <label for="name">Review Video (YouTube):</label>
                <input type="text" id="videoID" name="videoID" value="https://www.youtube.com/watch?v=<?php echo isset($videoID) ? $videoID : ''; ?>" required><br>
                <label for="name">Total Value:</label>
                <input type="text" id="total_value" name="total_value" value="<?php echo isset($total) ? $total : ''; ?>" required><br>
                <input type="submit" value="Submit">
                
            </form>
            <h2>Search Query</h2>
            <div style="display: flex; align-items: center;">
                <input type="text" id="searchQuery" placeholder="Ask your question..." style="flex: 1;margin-bottom: 0px;">
                <button onclick="searchQuery()" style="margin-left: 10px;">Search</button>
            </div>
            <div class="search-results" id="searchResults"></div>
        </div>
        

        <script>
            function searchQuery() {
                const query = document.getElementById('searchQuery').value;
                const resultsContainer = document.getElementById('searchResults');
                resultsContainer.innerHTML = '<p>Processing...</p>'; // Clear previous results

                if (query.trim() === '') {
                    resultsContainer.innerHTML = '<p>Please enter a question.</p>';
                    return;
                }
                
                const requestData = {
                    pdf_path: '<?php echo $pdf_path; ?>',
                    query: query
                };

                fetch('http://localhost:5000/query_from_invoice', {
                    method: 'POST',
                    body: JSON.stringify(requestData),
                    headers: {
                        'Content-Type': 'application/json' // Ensure correct Content-Type
                    }
                })
                .then(response => response.json())
                .then(data => {
                    // Display results in searchResults div
                    const searchResults = document.getElementById('searchResults');
                    searchResults.innerHTML = '<h3>Answer:</h3><p>' + data.query + '</p>';
                })
                .catch(error => {
                    console.error('Error:', error);
                    const searchResults = document.getElementById('searchResults');
                    searchResults.innerHTML = '<p>There was an error processing your request.</p>';
                });
            }
        </script>
    </div>
</body>
</html>
