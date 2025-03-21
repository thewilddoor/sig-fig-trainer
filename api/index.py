from flask import Flask, render_template, request, jsonify, session
import random
import math
import secrets
import re

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

#---------- Significant Figures Functions ----------#

def generate_random_number(hard_mode=False):
    """Generate a random number in various formats to test significant figures."""
    formats = [
        # Format: (min, max, decimal_places, scientific_notation)
        (0, 10, 0, False),           # Integers: 0-10
        (0, 10, 3, False),           # Decimals: 0.000-10.000
        (10, 1000, 2, False),        # Larger numbers with decimals
        (0.001, 0.999, 5, False),    # Small decimals
        (100, 9999, 0, False),       # Larger integers
        (1, 100, 4, True),           # Scientific notation
        (0.001, 0.999, 3, True)      # Small numbers in scientific notation
    ]
    
    # Hard mode adds tricky cases
    hard_formats = [
        # Format: (min, max, decimal_places, scientific_notation, type)
        (100, 9999, 0, False, "trailing_zeros"),  # Numbers with trailing zeros (no decimal)
        (0.001, 0.1, 5, False, "leading_zeros"),  # Numbers with many leading zeros
        (1000, 9999, 2, False, "exact_zeros"),    # Numbers with exact zeros (0 in the middle)
        (1, 10, 6, False, "exact_trailing"),      # Numbers with exact trailing zeros
        (0, 0, 0, False, "zero"),                 # Zero in different forms
    ]
    
    if hard_mode and random.random() < 0.7:  # 70% chance of hard format in hard mode
        choice_type = random.choice(hard_formats)
        min_val, max_val, decimal_places, scientific, format_type = choice_type
        
        # Generate the number
        num = random.uniform(min_val, max_val)
        
        # Handle special tricky cases
        if format_type == "trailing_zeros":
            # Generate a number with trailing zeros but no decimal point
            num = random.randint(min_val, max_val)
            num = num - (num % 10**random.randint(1, 3))  # Make it end with 0s
            return str(num)
            
        elif format_type == "leading_zeros":
            # Generate a number with many leading zeros
            decimal_part = str(random.randint(1, 999)).rjust(3, '0')
            leading_zeros = '0' * random.randint(2, 5)
            return f"0.{leading_zeros}{decimal_part}"
            
        elif format_type == "exact_zeros":
            # Generate a number with zeros in the middle
            num = random.randint(1000, 9999)
            num_str = str(num)
            pos = random.randint(1, 2)
            num_str = num_str[:pos] + '0' * random.randint(1, 2) + num_str[pos+1:]
            if random.random() < 0.5:  # 50% chance to add a decimal point
                pos = random.randint(0, len(num_str))
                return num_str[:pos] + '.' + num_str[pos:]
            return num_str
            
        elif format_type == "exact_trailing":
            # Numbers with trailing zeros after decimal point
            base = random.randint(1, 10)
            trailing = '0' * random.randint(2, 5)
            return f"{base}.{trailing}"
            
        elif format_type == "zero":
            # Various forms of zero
            zero_formats = [
                "0", "0.0", "0.00", "0.000", 
                "0.0e0", "0e0", "0.00e-10", "0.000e+5"
            ]
            return random.choice(zero_formats)
    
    # Default format (or non-hard specific cases in hard mode)
    choice = random.choice(formats)
    min_val, max_val, decimal_places, scientific = choice
    
    # Generate the number
    num = random.uniform(min_val, max_val)
    
    # Format the number
    if scientific:
        formatted_num = f"{num:.{decimal_places}e}"
    else:
        formatted_num = f"{num:.{decimal_places}f}"
    
    # Sometimes add trailing zeros
    if random.random() < 0.3 and not scientific and '.' in formatted_num:
        formatted_num += "0" * random.randint(1, 3)
    
    # Sometimes add leading zeros
    if random.random() < 0.3 and abs(num) < 1 and not scientific:
        integer_part = formatted_num.split('.')[0]
        if integer_part == '0':
            decimal_part = formatted_num.split('.')[1]
            leading_zeros = '0' * random.randint(1, 3)
            formatted_num = f"0.{leading_zeros}{decimal_part}"
    
    return formatted_num

def count_sig_figs(number_str):
    """Count the significant figures in a number."""
    # Remove the sign if present
    number_str = number_str.strip().replace('+', '').replace('-', '')
    
    # Handle scientific notation
    if 'e' in number_str.lower():
        base, _ = number_str.lower().split('e')
        return count_sig_figs(base)
    
    # Special case for zero
    if float(number_str) == 0:
        # A single zero has one sig fig; with decimal point, count trailing zeros
        if '.' in number_str:
            # Count after the decimal point (all zeros after decimal are significant)
            decimal_part = number_str.split('.')[1]
            if all(c == '0' for c in decimal_part):
                return len(decimal_part)
            # If there are non-zero digits after decimal, standard rules apply
        return 1
    
    # Check if there's a decimal point
    has_decimal = '.' in number_str
    
    if has_decimal:
        # Remove the decimal point for counting
        number_without_decimal = number_str.replace('.', '')
        
        # Remove leading zeros
        number_without_decimal = number_without_decimal.lstrip('0')
        
        # All digits are significant (trailing zeros included)
        return len(number_without_decimal)
    else:
        # No decimal point
        # Remove trailing zeros (not significant)
        trimmed = number_str.rstrip('0')
        
        # Count significant figures
        return len(trimmed)

def explain_sig_figs(number_str, user_answer):
    """Provide an explanation of why the answer is correct or incorrect."""
    correct_count = count_sig_figs(number_str)
    try:
        user_count = int(user_answer)
        
        # Prepare explanation
        explanation = f"The number {number_str} has {correct_count} significant figures because:\n"
        
        # Case-by-case analysis
        if 'e' in number_str.lower():
            # Scientific notation
            base, _ = number_str.lower().split('e')
            explanation += "- In scientific notation, only the digits in the coefficient (before the 'e') count\n"
            explanation += f"- The coefficient {base} has {count_sig_figs(base)} significant figures"
        
        elif '.' in number_str:
            # Decimal point present
            
            # Check for leading zeros
            if number_str.startswith('0.'):
                explanation += "- Leading zeros (before any non-zero digit) are NOT significant\n"
                
                # Count leading zeros
                decimal_part = number_str.split('.')[1]
                leading_zero_count = 0
                for digit in decimal_part:
                    if digit == '0':
                        leading_zero_count += 1
                    else:
                        break
                        
                if leading_zero_count > 0:
                    explanation += f"- The {leading_zero_count} leading zero(s) after the decimal point are NOT significant\n"
                
            # Check for trailing zeros
            if number_str.endswith('0'):
                explanation += "- When a decimal point is shown, ALL trailing zeros ARE significant\n"
                
            # Check for zeros in the middle
            if '0' in number_str[1:-1]:  # Exclude first and last character
                explanation += "- All zeros between significant digits ARE significant\n"
                
            explanation += "- When a decimal point is present, we count all digits except leading zeros"
            
        else:
            # No decimal point
            
            # Check for trailing zeros
            if number_str.endswith('0'):
                zero_count = len(number_str) - len(number_str.rstrip('0'))
                explanation += f"- Without a decimal point, the {zero_count} trailing zero(s) are NOT significant\n"
                explanation += "- To make trailing zeros significant, either add a decimal point or use scientific notation"
                
            # Check for zeros in the middle
            elif '0' in number_str[1:]:  # Exclude first character
                explanation += "- All zeros between significant digits ARE significant\n"
                explanation += "- Count all non-zero digits and all zeros that are between significant digits"
                
            else:
                explanation += "- Count all non-zero digits"
                
        # Explain common error if user is wrong
        if user_count != correct_count:
            if user_count > correct_count:
                if number_str.startswith('0.'):
                    explanation += "\n\nYou may have counted the leading zeros, which are NOT significant."
                elif not '.' in number_str and number_str.endswith('0'):
                    explanation += "\n\nYou may have counted trailing zeros in a number without a decimal point, which are NOT significant."
            elif user_count < correct_count:
                if '0' in number_str[1:-1]:
                    explanation += "\n\nYou may have missed counting zeros between significant digits, which ARE significant."
                elif '.' in number_str and number_str.endswith('0'):
                    explanation += "\n\nYou may have missed counting trailing zeros in a number with a decimal point, which ARE significant."
            
        return explanation
    
    except ValueError:
        return f"The number {number_str} has {correct_count} significant figures."

def check_answer(number_str, user_answer):
    """Check if the user's answer matches the correct count of significant figures."""
    correct_count = count_sig_figs(number_str)
    
    try:
        user_count = int(user_answer)
        return user_count == correct_count, correct_count
    except ValueError:
        return False, correct_count

def generate_sig_fig_operation(hard_mode=False):
    """Generate a calculation that involves significant figures."""
    operations = ['+', '-', '*', '/']
    
    if hard_mode:
        # More complex operations in hard mode
        op_choices = random.choices(operations, weights=[1, 1, 3, 3], k=1)[0]
    else:
        # More basic operations in normal mode
        op_choices = random.choices(operations, weights=[2, 2, 1, 1], k=1)[0]
    
    num1 = generate_random_number(hard_mode)
    num2 = generate_random_number(hard_mode)
    
    expression = f"{num1} {op_choices} {num2}"
    
    # Calculate the result with appropriate sig figs
    val1 = float(num1)
    val2 = float(num2)
    
    if op_choices == '+':
        # Addition: result has same number of decimal places as least precise number
        decimal_places1 = len(num1.split('.')[-1]) if '.' in num1 else 0
        decimal_places2 = len(num2.split('.')[-1]) if '.' in num2 else 0
        min_decimal_places = min(decimal_places1, decimal_places2)
        raw_result = val1 + val2
        result = round(raw_result, min_decimal_places)
        
    elif op_choices == '-':
        # Subtraction: result has same number of decimal places as least precise number
        decimal_places1 = len(num1.split('.')[-1]) if '.' in num1 else 0
        decimal_places2 = len(num2.split('.')[-1]) if '.' in num2 else 0
        min_decimal_places = min(decimal_places1, decimal_places2)
        raw_result = val1 - val2
        result = round(raw_result, min_decimal_places)
        
    elif op_choices == '*':
        # Multiplication: result has same number of sig figs as least precise number
        sig_figs1 = count_sig_figs(num1)
        sig_figs2 = count_sig_figs(num2)
        min_sig_figs = min(sig_figs1, sig_figs2)
        raw_result = val1 * val2
        
        # Format to correct sig figs
        if raw_result == 0:
            result = 0
        else:
            magnitude = math.floor(math.log10(abs(raw_result)))
            rounded = round(raw_result / (10 ** magnitude), min_sig_figs - 1) * (10 ** magnitude)
            result = rounded
        
    elif op_choices == '/':
        # Division: result has same number of sig figs as least precise number
        sig_figs1 = count_sig_figs(num1)
        sig_figs2 = count_sig_figs(num2)
        min_sig_figs = min(sig_figs1, sig_figs2)
        raw_result = val1 / val2
        
        # Format to correct sig figs
        if raw_result == 0:
            result = 0
        else:
            magnitude = math.floor(math.log10(abs(raw_result)))
            rounded = round(raw_result / (10 ** magnitude), min_sig_figs - 1) * (10 ** magnitude)
            result = rounded
    
    # Format nicely for display
    if abs(result) < 0.001 or abs(result) > 10000:
        result_str = f"{result:.6e}"
    else:
        result_str = f"{result:.6f}".rstrip('0').rstrip('.') if '.' in f"{result:.6f}" else f"{int(result)}"
    
    return expression, result_str, op_choices

def explain_calculation_sig_figs(expression, result, operation, user_input):
    """Explain why the calculated result has the correct number of significant figures."""
    parts = expression.split()
    num1, num2 = parts[0], parts[2]
    
    explanation = f"For the expression {expression}:\n"
    
    # Explain the sig fig rules for the operation
    if operation in ['+', '-']:
        decimal_places1 = len(num1.split('.')[-1]) if '.' in num1 else 0
        decimal_places2 = len(num2.split('.')[-1]) if '.' in num2 else 0
        min_decimal_places = min(decimal_places1, decimal_places2)
        
        explanation += f"- Addition and subtraction follow the decimal places rule\n"
        explanation += f"- The first number has {decimal_places1} decimal places\n"
        explanation += f"- The second number has {decimal_places2} decimal places\n"
        explanation += f"- The result should have {min_decimal_places} decimal places (limited by the least precise number)\n"
        
    elif operation in ['*', '/']:
        sig_figs1 = count_sig_figs(num1)
        sig_figs2 = count_sig_figs(num2)
        min_sig_figs = min(sig_figs1, sig_figs2)
        
        explanation += f"- Multiplication and division follow the significant figures rule\n"
        explanation += f"- The first number has {sig_figs1} significant figures\n"
        explanation += f"- The second number has {sig_figs2} significant figures\n"
        explanation += f"- The result should have {min_sig_figs} significant figures (limited by the least precise number)\n"
    
    # Compare to user's answer
    try:
        user_value = float(user_input.replace(' ', ''))
        result_value = float(result)
        
        # Check if the values are close
        values_match = abs((user_value - result_value) / max(abs(result_value), 1e-10)) < 0.001
        
        # Check if significant figures match
        sig_fig_match = count_sig_figs(user_input) == count_sig_figs(result)
        
        if not values_match:
            explanation += f"\nYour calculation result ({user_value}) differs from the correct value ({result_value})."
        
        if not sig_fig_match:
            explanation += f"\nYour answer has {count_sig_figs(user_input)} significant figures, but it should have {count_sig_figs(result)} significant figures."
            
            if operation in ['+', '-'] and '.' in user_input and '.' in result:
                user_decimal = len(user_input.split('.')[-1]) if '.' in user_input else 0
                result_decimal = len(result.split('.')[-1]) if '.' in result else 0
                if user_decimal != result_decimal:
                    explanation += f"\nFor addition/subtraction, check your decimal places: you have {user_decimal} but should have {result_decimal}."
                    
    except ValueError:
        explanation += "\nCouldn't analyze your answer because it's not in a valid number format."
        
    explanation += f"\n\nThe correct answer with proper significant figures is: {result}"
    return explanation

#---------- Flask Routes ----------#

@app.route('/')
def index():
    # Initialize session variables if they don't exist
    if 'score' not in session:
        session['score'] = 0
    if 'total_questions' not in session:
        session['total_questions'] = 0
    if 'hard_mode' not in session:
        session['hard_mode'] = False
        
    return render_template('index.html', 
                          score=session['score'], 
                          total=session['total_questions'],
                          hard_mode=session['hard_mode'])

@app.route('/set_mode', methods=['POST'])
def set_mode():
    data = request.get_json()
    session['hard_mode'] = data.get('hard_mode', False)
    # Reset score when changing modes
    session['score'] = 0
    session['total_questions'] = 0
    return jsonify({'status': 'success', 'hard_mode': session['hard_mode']})

@app.route('/get_question', methods=['GET'])
def get_question():
    # Decide whether to generate a counting question or a calculation question
    hard_mode = session.get('hard_mode', False)
    
    if hard_mode and random.random() < 0.6:  # 60% chance in hard mode for calculation
        expression, result, operation = generate_sig_fig_operation(hard_mode)
        return jsonify({
            'type': 'calculation',
            'question': expression,
            'answer': result,
            'operation': operation
        })
    else:
        number = generate_random_number(hard_mode)
        correct_count = count_sig_figs(number)
        return jsonify({
            'type': 'counting',
            'question': number,
            'answer': correct_count
        })

@app.route('/check_answer', methods=['POST'])
def check_answer_route():
    data = request.get_json()
    question_type = data.get('type')
    user_answer = data.get('answer')
    
    if question_type == 'counting':
        number = data.get('question')
        is_correct, correct_count = check_answer(number, user_answer)
        explanation = explain_sig_figs(number, user_answer)
        
        if is_correct:
            session['score'] = session.get('score', 0) + 1
        session['total_questions'] = session.get('total_questions', 0) + 1
        
        return jsonify({
            'correct': is_correct,
            'correct_answer': correct_count,
            'explanation': explanation,
            'score': session['score'],
            'total': session['total_questions']
        })
        
    elif question_type == 'calculation':
        expression = data.get('question')
        correct_result = data.get('correct_answer')
        operation = data.get('operation')
        
        # Check if values are close
        try:
            user_value = float(user_answer.replace(' ', ''))
            correct_value = float(correct_result)
            values_match = abs((user_value - correct_value) / max(abs(correct_value), 1e-10)) < 0.001
        except ValueError:
            values_match = False
            
        # Check sig fig match
        try:
            sig_fig_match = count_sig_figs(user_answer) == count_sig_figs(correct_result)
        except:
            sig_fig_match = False
            
        is_correct = values_match and sig_fig_match
        explanation = explain_calculation_sig_figs(expression, correct_result, operation, user_answer)
        
        if is_correct:
            session['score'] = session.get('score', 0) + 1
        session['total_questions'] = session.get('total_questions', 0) + 1
        
        return jsonify({
            'correct': is_correct,
            'correct_answer': correct_result,
            'explanation': explanation,
            'score': session['score'],
            'total': session['total_questions'],
            'values_match': values_match,
            'sig_fig_match': sig_fig_match
        })
    
    return jsonify({'error': 'Invalid question type'})

@app.route('/reset_score', methods=['POST'])
def reset_score():
    session['score'] = 0
    session['total_questions'] = 0
    return jsonify({'status': 'success'})

#---------- HTML Templates ----------#

# This is a workaround to include the HTML template in the single file
@app.route('/templates/index.html')
def serve_template():
    return render_template('index.html')

# Create the template folder and index.html file
import os
if not os.path.exists('templates'):
    os.makedirs('templates')

with open('templates/index.html', 'w') as f:
    f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Significant Figures Practice</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
            padding-top: 2rem;
        }
        .container {
            max-width: 800px;
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 2rem;
            margin-bottom: 2rem;
        }
        h1 {
            color: #0d6efd;
            margin-bottom: 1.5rem;
        }
        .question-container {
            margin-top: 2rem;
            padding: 1.5rem;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            background-color: #f8f9fa;
        }
        .number {
            font-family: monospace;
            font-size: 1.5rem;
            font-weight: bold;
            color: #0d6efd;
            padding: 0.5rem;
            background-color: #e9ecef;
            border-radius: 5px;
            margin: 1rem 0;
            display: inline-block;
        }
        .feedback {
            margin-top: 1.5rem;
            padding: 1rem;
            border-radius: 8px;
        }
        .correct {
            background-color: #d4edda;
            color: #155724;
        }
        .incorrect {
            background-color: #f8d7da;
            color: #721c24;
        }
        .explanation {
            margin-top: 1.5rem;
            background-color: #e9ecef;
            padding: 1rem;
            border-radius: 8px;
            white-space: pre-line;
        }
        .form-check-input:checked {
            background-color: #0d6efd;
        }
        .score-container {
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .score {
            font-size: 1.2rem;
            font-weight: bold;
            color: #0d6efd;
        }
        .reset-btn {
            margin-left: 1rem;
        }
        .mode-setting {
            margin-bottom: 1.5rem;
        }
        .question-box {
            margin-bottom: 1rem;
            font-size: 1.25rem;
        }
        .formula {
            font-family: monospace;
            font-weight: bold;
        }
        #question-display {
            margin-bottom: 1.5rem;
        }
        @media (max-width: 576px) {
            .container {
                padding: 1rem;
            }
            .number {
                font-size: 1.2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center">Significant Figures Practice</h1>
        
        <!-- Mode Selection -->
        <div class="mode-setting">
            <div class="form-check form-switch">
                <input class="form-check-input" type="checkbox" id="hardModeToggle">
                <label class="form-check-label" for="hardModeToggle">
                    Hard Mode 
                    <span class="badge bg-danger" id="hardModeIndicator" style="display: none;">ACTIVE</span>
                </label>
            </div>
            <small class="form-text text-muted">Hard mode includes tricky numbers and calculations with significant figures.</small>
        </div>

        <!-- Score Display -->
        <div class="score-container">
            <span class="score">Score: <span id="score">0</span>/<span id="total-questions">0</span> 
                (<span id="percentage">0</span>%)
            </span>
            <button id="reset-score" class="btn btn-sm btn-outline-secondary reset-btn">
                Reset Score
            </button>
        </div>

        <!-- Question Section -->
        <div class="question-container">
            <div id="question-display">
                <div class="question-box">
                    <span id="question-text">Click "New Question" to start</span>
                </div>
                <div class="number" id="number-display" style="display: none;"></div>
            </div>

            <div class="input-group mb-3">
                <input type="text" class="form-control" id="answer-input" placeholder="Your answer">
                <button class="btn btn-primary" id="submit-btn">Submit</button>
            </div>

            <div class="feedback" id="feedback" style="display: none;"></div>
            <div class="explanation" id="explanation" style="display: none;"></div>
            
            <div class="d-grid gap-2 mt-4">
                <button class="btn btn-success" id="next-question">New Question</button>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // DOM elements
            const hardModeToggle = document.getElementById('hardModeToggle');
            const hardModeIndicator = document.getElementById('hardModeIndicator');
            const questionText = document.getElementById('question-text');
            const numberDisplay = document.getElementById('number-display');
            const answerInput = document.getElementById('answer-input');
            const submitBtn = document.getElementById('submit-btn');
            const feedbackDiv = document.getElementById('feedback');
            const explanationDiv = document.getElementById('explanation');
            const nextQuestionBtn = document.getElementById('next-question');
            const resetScoreBtn = document.getElementById('reset-score');
            const scoreDisplay = document.getElementById('score');
            const totalQuestionsDisplay = document.getElementById('total-questions');
            const percentageDisplay = document.getElementById('percentage');
            
            // State variables
            let currentQuestion = null;
            
            // Initialize hard mode toggle based on server state
            hardModeToggle.checked = {{ 'true' if hard_mode else 'false' }};
            hardModeIndicator.style.display = hardModeToggle.checked ? 'inline' : 'none';
            
            // Update score display
            function updateScoreDisplay(score, total) {
                scoreDisplay.textContent = score;
                totalQuestionsDisplay.textContent = total;
                const percentage = total > 0 ? Math.round((score / total) * 100) : 0;
                percentageDisplay.textContent = percentage;
            }
            
            // Initialize score
            updateScoreDisplay({{ score }}, {{ total }});
            
            // Toggle hard mode
            hardModeToggle.addEventListener('change', function() {
                const hardMode = this.checked;
                hardModeIndicator.style.display = hardMode ? 'inline' : 'none';
                
                // Update server setting
                fetch('/set_mode', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({hard_mode: hardMode}),
                })
                .then(response => response.json())
                .then(data => {
                    // Reset the score display
                    updateScoreDisplay(0, 0);
                })
                .catch(error => {
                    console.error('Error setting mode:', error);
                });
            });
            
            // Reset score
            resetScoreBtn.addEventListener('click', function() {
                fetch('/reset_score', {
                    method: 'POST',
                })
                .then(response => response.json())
                .then(data => {
                    updateScoreDisplay(0, 0);
                })
                .catch(error => {
                    console.error('Error resetting score:', error);
                });
            });
            
            // Get a new question
            function getNewQuestion() {
                // Reset UI
                answerInput.value = '';
                feedbackDiv.style.display = 'none';
                explanationDiv.style.display = 'none';
                answerInput.disabled = false;
                submitBtn.disabled = false;
                
                fetch('/get_question')
                .then(response => response.json())
                .then(data => {
                    currentQuestion = data;
                    
                    if (data.type === 'counting') {
                        // Display counting question
                        questionText.textContent = "How many significant figures are in this number?";
                        numberDisplay.textContent = data.question;
                        numberDisplay.style.display = 'inline-block';
                    } else if (data.type === 'calculation') {
                        // Display calculation question
                        questionText.textContent = "Calculate and express the answer with the correct significant figures:";
                        numberDisplay.textContent = data.question;
                        numberDisplay.style.display = 'inline-block';
                    }
                })
                .catch(error => {
                    console.error('Error getting new question:', error);
                });
            }
            
            nextQuestionBtn.addEventListener('click', getNewQuestion);
            
            // Submit answer
            submitBtn.addEventListener('click', function() {
                if (!currentQuestion) return;
                
                const answer = answerInput.value.trim();
                if (!answer) return;
                
                // Disable input while processing
                answerInput.disabled = true;
                submitBtn.disabled = true;
                
                fetch('/check_answer', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        type: currentQuestion.type,
                        question: currentQuestion.question,
                        answer: answer,
                        correct_answer: currentQuestion.answer,
                        operation: currentQuestion.operation
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    // Update score
                    updateScoreDisplay(data.score, data.total);
                    
                    // Show feedback
                    feedbackDiv.style.display = 'block';
                    feedbackDiv.className = data.correct ? 'feedback correct' : 'feedback incorrect';
                    
                    if (data.correct) {
                        feedbackDiv.innerHTML = '<strong>Correct!</strong> Good job! 👍';
                    } else {
                        if (currentQuestion.type === 'counting') {
                            feedbackDiv.innerHTML = `<strong>Incorrect.</strong> The number ${currentQuestion.question} has ${data.correct_answer} significant figures.`;
                        } else {
                            let feedbackText = '<strong>Incorrect.</strong> ';
                            
                            // For calculation, provide more detailed feedback
                            if (data.hasOwnProperty('values_match')) {
                                if (!data.values_match) {
                                    feedbackText += "Your calculation result is incorrect. ";
                                }
                                if (!data.sig_fig_match) {
                                    feedbackText += "Your significant figures are incorrect. ";
                                }
                            }
                            
                            feedbackText += `The correct answer is: ${data.correct_answer}`;
                            feedbackDiv.innerHTML = feedbackText;
                        }
                    }
                    
                    // Show explanation
                    explanationDiv.style.display = 'block';
                    explanationDiv.textContent = data.explanation;
                })
                .catch(error => {
                    console.error('Error checking answer:', error);
                    feedbackDiv.style.display = 'block';
                    feedbackDiv.className = 'feedback incorrect';
                    feedbackDiv.textContent = 'An error occurred. Please try again.';
                    
                    // Re-enable input
                    answerInput.disabled = false;
                    submitBtn.disabled = false;
                });
            });
            
            // Allow pressing Enter to submit answer
            answerInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    submitBtn.click();
                }
            });
        });
    </script>
</body>
</html>
    """)

#---------- Main Execution ----------#

if __name__ == '__main__':
    app.run(debug=True)
