from flask import Flask, render_template_string, request, jsonify
import random

app = Flask(__name__)

def generate_random_number(hard_mode=False):
    """Generate a random number for sig fig practice"""
    if not hard_mode:
        # Simple cases
        types = ['regular', 'decimal', 'scientific', 'zeros']
        num_type = random.choice(types)
        
        if num_type == 'regular':
            # Regular numbers: 123, 456, etc.
            digits = random.randint(1, 5)
            return str(random.randint(10**(digits-1), 10**digits - 1))
        elif num_type == 'decimal':
            # Decimal numbers: 0.123, 0.045, etc.
            digits = random.randint(1, 5)
            return str(random.random())[:digits+2]
        elif num_type == 'scientific':
            # Scientific notation: 1.23e5, 4.56e-3, etc.
            mantissa_digits = random.randint(1, 3)
            mantissa = random.random() * 9 + 1
            exponent = random.randint(-6, 6)
            return f"{mantissa:.{mantissa_digits}f}e{exponent}"
        else:  # zeros
            # Numbers with zeros: 1000, 0.0120, etc.
            base = random.randint(1, 9)
            zeros = random.randint(1, 4)
            position = random.choice(['leading', 'trailing', 'middle'])
            
            if position == 'leading':
                return '0.' + '0' * zeros + str(base) + str(random.randint(0, 999))
            elif position == 'trailing':
                return str(base) + str(random.randint(0, 99)) + '0' * zeros
            else:  # middle
                return str(base) + '0' * zeros + str(random.randint(1, 9))
    else:
        # Harder cases
        types = ['ambiguous_zeros', 'mixed_notation', 'exact_numbers', 'complex_decimals']
        num_type = random.choice(types)
        
        if num_type == 'ambiguous_zeros':
            # Numbers with ambiguous zeros: 1000, 0.0100, etc.
            base = random.randint(1, 9)
            zeros = random.randint(2, 5)
            return str(base) + '0' * zeros
        elif num_type == 'mixed_notation':
            # Mixed notation: 1.20e3, 4.00e-2, etc.
            mantissa_digits = random.randint(1, 3)
            mantissa = random.random() * 9 + 1
            trailing_zeros = random.randint(0, 2)
            exponent = random.randint(-6, 6)
            mantissa_str = f"{mantissa:.{mantissa_digits + trailing_zeros}f}"
            return f"{mantissa_str}e{exponent}"
        elif num_type == 'exact_numbers':
            # Numbers that might be exact: 100, 1000, etc.
            base = 10 ** random.randint(1, 4)
            return str(base)
        else:  # complex_decimals
            # Complex decimals: 0.00120300, etc.
            leading_zeros = random.randint(1, 3)
            middle_digits = random.randint(1, 3)
            trailing_zeros = random.randint(1, 3)
            middle = random.randint(1, 10**middle_digits - 1)
            return f"0.{'0' * leading_zeros}{middle}{'0' * trailing_zeros}"
            
    return "42"  # Default fallback

def count_sig_figs(number_str):
    """Count significant figures following standard rules."""
    # Normalize input
    number_str = str(number_str).strip().lower()
    
    # Special case for zero
    if float(number_str) == 0:
        return 1
    
    # Handle scientific notation
    if 'e' in number_str:
        mantissa, _ = number_str.split('e')
        return count_sig_figs(mantissa.strip())
    
    # Check if there's a decimal point
    has_decimal = '.' in number_str
    
    if has_decimal:
        # With decimal point
        parts = number_str.split('.')
        integer_part = parts[0]
        decimal_part = parts[1] if len(parts) > 1 else ""
        
        if integer_part == '' or integer_part == '0':
            # Number less than 1 (e.g., 0.00123)
            # Count from first non-zero digit in decimal part
            for i, digit in enumerate(decimal_part):
                if digit != '0':
                    # All digits from first non-zero to end are significant
                    return len(decimal_part) - i
            # All zeros
            return 1
        else:
            # Number with integer part (e.g., 123.456)
            # Remove leading zeros from integer part
            integer_part = integer_part.lstrip('0')
            # All digits from integer part and all decimal digits are significant
            return len(integer_part) + len(decimal_part)
    else:
        # No decimal point (e.g., 12300)
        # Leading zeros are not significant
        number_str = number_str.lstrip('0')
        # Trailing zeros are not significant without a decimal
        return len(number_str.rstrip('0'))

def explain_sig_figs(number_str, user_answer, correct_answer):
    """Explain why the user's answer is incorrect"""
    if user_answer == correct_answer:
        return "Correct! Good job."
        
    explanation = ""
    
    # Basic rules explanation
    if 'e' in number_str.lower():
        explanation += "In scientific notation, only the digits in the mantissa (the part before 'e') count for significant figures. "
    
    if '.' in number_str:
        if float(number_str) < 1:
            explanation += "For a decimal number less than 1, leading zeros are NOT significant. They only serve to locate the decimal point. "
        explanation += "When there's a decimal point, ALL trailing zeros ARE significant. "
    else:
        explanation += "Without a decimal point, trailing zeros are NOT significant (they could just be placeholders). "
    
    # More specific explanations based on the number
    if number_str.startswith('0.'):
        zero_count = 0
        for char in number_str[2:]:
            if char == '0':
                zero_count += 1
            else:
                break
        if zero_count > 0:
            explanation += f"The {zero_count} zero(s) after the decimal point but before the first non-zero digit are NOT significant. "
    
    if number_str.replace('.', '').strip('0') == '':
        explanation += "For zero, we generally consider it to have 1 significant figure. "
    
    explanation += f"The correct answer is {correct_answer} significant figures."
    
    return explanation

# HTML template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Significant Figures Practice</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f7fa;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        .number-display {
            font-size: 2.5rem;
            text-align: center;
            margin: 30px 0;
            font-family: 'Courier New', monospace;
            background-color: #e9f7fe;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #b3e0ff;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="number"], button {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            cursor: pointer;
            margin-top: 10px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 4px;
        }
        .correct {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .incorrect {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .explanation {
            margin-top: 10px;
            font-style: italic;
        }
        .mode-toggle {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }
        .toggle-label {
            margin-right: 10px;
            display: flex;
            align-items: center;
        }
        .stats {
            text-align: center;
            margin-top: 20px;
            font-weight: bold;
        }
        .hidden {
            display: none;
        }
        @media (max-width: 600px) {
            body {
                padding: 10px;
            }
            .number-display {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Significant Figures Practice</h1>
        
        <div class="mode-toggle">
            <div class="toggle-label">
                <input type="checkbox" id="hard-mode">
                <span>Hard Mode</span>
            </div>
        </div>
        
        <div id="problem">
            <p>How many significant figures are in this number?</p>
            <div class="number-display" id="number">--</div>
            
            <div class="form-group">
                <label for="user-answer">Your Answer:</label>
                <input type="number" id="user-answer" min="0" step="1">
            </div>
            
            <button id="check-answer">Check Answer</button>
            <button id="new-problem">New Problem</button>
            
            <div id="result" class="result hidden"></div>
        </div>
        
        <div class="stats">
            <p>Score: <span id="correct-count">0</span> / <span id="total-count">0</span></p>
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const numberDisplay = document.getElementById('number');
            const userAnswerInput = document.getElementById('user-answer');
            const checkAnswerButton = document.getElementById('check-answer');
            const newProblemButton = document.getElementById('new-problem');
            const resultDiv = document.getElementById('result');
            const hardModeCheckbox = document.getElementById('hard-mode');
            const correctCountSpan = document.getElementById('correct-count');
            const totalCountSpan = document.getElementById('total-count');
            
            let currentNumber = '';
            let correctAnswer = 0;
            let correctCount = 0;
            let totalCount = 0;
            
            // Generate a new problem when the page loads
            generateNewProblem();
            
            // Event listener for the "Check Answer" button
            checkAnswerButton.addEventListener('click', function() {
                checkAnswer();
            });
            
            // Allow pressing Enter to submit answer
            userAnswerInput.addEventListener('keyup', function(event) {
                if (event.key === 'Enter') {
                    checkAnswer();
                }
            });
            
            // Event listener for the "New Problem" button
            newProblemButton.addEventListener('click', function() {
                generateNewProblem();
            });
            
            function generateNewProblem() {
                const hardMode = hardModeCheckbox.checked;
                
                fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ hard_mode: hardMode })
                })
                .then(response => response.json())
                .then(data => {
                    currentNumber = data.number;
                    correctAnswer = data.correct_answer;
                    
                    numberDisplay.textContent = currentNumber;
                    userAnswerInput.value = '';
                    resultDiv.classList.add('hidden');
                    
                    // Focus the input field for better UX
                    userAnswerInput.focus();
                })
                .catch(error => {
                    console.error('Error generating problem:', error);
                    alert('Error generating problem. Please try again.');
                });
            }
            
            function checkAnswer() {
                const userAnswer = parseInt(userAnswerInput.value, 10);
                
                if (isNaN(userAnswer)) {
                    alert('Please enter a valid number.');
                    return;
                }
                
                fetch('/check', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        number: currentNumber,
                        user_answer: userAnswer
                    })
                })
                .then(response => response.json())
                .then(data => {
                    totalCount++;
                    totalCountSpan.textContent = totalCount;
                    
                    if (data.correct) {
                        resultDiv.className = 'result correct';
                        resultDiv.innerHTML = '<strong>Correct!</strong>';
                        correctCount++;
                        correctCountSpan.textContent = correctCount;
                    } else {
                        resultDiv.className = 'result incorrect';
                        resultDiv.innerHTML = `<strong>Incorrect.</strong> <div class="explanation">${data.explanation}</div>`;
                    }
                    
                    resultDiv.classList.remove('hidden');
                })
                .catch(error => {
                    console.error('Error checking answer:', error);
                    alert('Error checking answer. Please try again.');
                });
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/generate', methods=['POST'])
def generate():
    hard_mode = request.json.get('hard_mode', False)
    number = generate_random_number(hard_mode)
    correct_answer = count_sig_figs(number)
    return jsonify({
        'number': number,
        'correct_answer': correct_answer
    })

@app.route('/check', methods=['POST'])
def check():
    number = request.json.get('number')
    user_answer = int(request.json.get('user_answer'))
    correct_answer = count_sig_figs(number)
    explanation = explain_sig_figs(number, user_answer, correct_answer)
    return jsonify({
        'correct': user_answer == correct_answer,
        'explanation': explanation
    })

# This avoids running the app when imported
# For Vercel deployment
app = app
