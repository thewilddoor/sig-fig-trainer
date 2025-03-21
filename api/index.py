from flask import Flask, render_template_string, request, jsonify
import random
import math

app = Flask(__name__)

def generate_random_number(hard_mode=False):
    """Generate a random number or calculation for sig fig practice"""
    if not hard_mode:
        # Simple mode - just counting sig figs in numbers
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
        # Hard mode - calculations with sig figs
        calculation_type = random.choice(['add_subtract', 'multiply_divide', 'mixed_operations', 'power_sqrt'])
        
        if calculation_type == 'add_subtract':
            # Addition/Subtraction (decimal places rule)
            num1 = random.uniform(0.1, 100)
            num2 = random.uniform(0.1, 100)
            decimal_places1 = random.randint(1, 3)
            decimal_places2 = random.randint(1, 3)
            num1_str = f"{num1:.{decimal_places1}f}"
            num2_str = f"{num2:.{decimal_places2}f}"
            operation = random.choice(['+', '-'])
            
            problem = {
                'type': 'calculation',
                'operation': 'add_subtract',
                'problem': f"{num1_str} {operation} {num2_str}",
                'num1': num1_str,
                'num2': num2_str,
                'op': operation
            }
            return problem
            
        elif calculation_type == 'multiply_divide':
            # Multiplication/Division (significant figures rule)
            sig_figs1 = random.randint(2, 3)
            sig_figs2 = random.randint(2, 3)
            
            # Generate numbers with specific sig figs
            num1 = random.uniform(1, 100)
            num2 = random.uniform(1, 100)
            num1_str = format_with_sig_figs(num1, sig_figs1)
            num2_str = format_with_sig_figs(num2, sig_figs2)
            
            operation = random.choice(['×', '÷'])
            
            problem = {
                'type': 'calculation',
                'operation': 'multiply_divide',
                'problem': f"{num1_str} {operation} {num2_str}",
                'num1': num1_str,
                'num2': num2_str,
                'op': operation
            }
            return problem
            
        elif calculation_type == 'mixed_operations':
            # Mixed operations
            sig_figs1 = random.randint(2, 3)
            sig_figs2 = random.randint(2, 3)
            sig_figs3 = random.randint(2, 3)
            
            num1 = random.uniform(1, 50)
            num2 = random.uniform(1, 50)
            num3 = random.uniform(1, 50)
            
            num1_str = format_with_sig_figs(num1, sig_figs1)
            num2_str = format_with_sig_figs(num2, sig_figs2)
            num3_str = format_with_sig_figs(num3, sig_figs3)
            
            op_types = random.choice([
                ('+', '×'),  # A + B × C
                ('×', '+'),  # A × B + C
                ('×', '÷'),  # A × B ÷ C
                ('÷', '+')   # A ÷ B + C
            ])
            
            problem = {
                'type': 'calculation',
                'operation': 'mixed',
                'problem': f"{num1_str} {op_types[0]} {num2_str} {op_types[1]} {num3_str}",
                'num1': num1_str,
                'num2': num2_str,
                'num3': num3_str,
                'op1': op_types[0],
                'op2': op_types[1]
            }
            return problem
            
        else:  # power_sqrt
            # Power or Square Root
            sub_type = random.choice(['power', 'sqrt'])
            
            if sub_type == 'power':
                base = random.uniform(1, 10)
                sig_figs = random.randint(2, 3)
                power = random.randint(2, 3)
                base_str = format_with_sig_figs(base, sig_figs)
                
                problem = {
                    'type': 'calculation',
                    'operation': 'power',
                    'problem': f"{base_str}^{power}",
                    'base': base_str,
                    'power': power
                }
                return problem
            else:  # sqrt
                num = random.uniform(1, 100)
                sig_figs = random.randint(2, 3)
                num_str = format_with_sig_figs(num, sig_figs)
                
                problem = {
                    'type': 'calculation',
                    'operation': 'sqrt',
                    'problem': f"√{num_str}",
                    'num': num_str
                }
                return problem
                
    return "42"  # Default fallback

def format_with_sig_figs(number, sig_figs):
    """Format a number with a specific number of significant figures"""
    if number == 0:
        return "0" + "." + "0" * (sig_figs - 1) if sig_figs > 1 else "0"
    
    # Determine the format string based on the magnitude
    magnitude = math.floor(math.log10(abs(number)))
    
    if magnitude >= sig_figs - 1:
        # Large number, use standard notation
        if magnitude < 5:  # Keep using standard notation for reasonable numbers
            # For numbers like 1200, 34000, etc.
            # Fix for proper rounding to sig figs for large numbers
            scale = 10 ** magnitude
            rounded = round(number / scale, sig_figs - 1) * scale
            return f"{rounded:.0f}"
        else:
            # Use scientific notation for very large numbers
            return f"{number:.{sig_figs-1}e}"
    elif magnitude >= 0:
        # Medium number
        return f"{number:.{sig_figs-1-magnitude}f}"
    else:
        # Small number
        return f"{number:.{sig_figs+abs(magnitude)-1}f}"

def calculate_result_and_sig_figs(problem):
    """Calculate the result and determine correct significant figures"""
    if problem['type'] != 'calculation':
        return None, count_sig_figs(problem)
    
    if problem['operation'] == 'add_subtract':
        num1 = float(problem['num1'])
        num2 = float(problem['num2'])
        op = problem['op']
        
        # Perform the calculation
        if op == '+':
            result = num1 + num2
        else:  # '-'
            result = num1 - num2
            
        # Determine decimal places
        dp1 = len(problem['num1'].split('.')[-1]) if '.' in problem['num1'] else 0
        dp2 = len(problem['num2'].split('.')[-1]) if '.' in problem['num2'] else 0
        min_dp = min(dp1, dp2)
        
        # Format result with correct decimal places
        formatted_result = f"{result:.{min_dp}f}"
        
        # Store both the exact value and the formatted result
        return {
            'exact': result,
            'formatted': formatted_result,
            'required_dp': min_dp,
            'sig_figs': count_sig_figs(formatted_result)
        }
    
    elif problem['operation'] == 'multiply_divide':
        num1 = float(problem['num1'])
        num2 = float(problem['num2'])
        op = problem['op']
        
        # Perform the calculation
        if op == '×':
            result = num1 * num2
        else:  # '÷'
            result = num1 / num2
            
        # Determine sig figs
        sf1 = count_sig_figs(problem['num1'])
        sf2 = count_sig_figs(problem['num2'])
        min_sf = min(sf1, sf2)
        
        # Format result with correct sig figs
        formatted_result = format_with_sig_figs(result, min_sf)
        
        return {
            'exact': result,
            'formatted': formatted_result,
            'required_sf': min_sf,
            'sig_figs': min_sf
        }
    
    elif problem['operation'] == 'mixed':
        num1 = float(problem['num1'])
        num2 = float(problem['num2'])
        num3 = float(problem['num3'])
        op1 = problem['op1']
        op2 = problem['op2']
        
        # Calculate based on operation precedence
        if (op1 in ['×', '÷']) and (op2 in ['+', '-']):
            # First calculate num1 op1 num2, then result op2 num3
            if op1 == '×':
                intermediate = num1 * num2
            else:
                intermediate = num1 / num2
                
            sf1 = count_sig_figs(problem['num1'])
            sf2 = count_sig_figs(problem['num2'])
            intermediate_sf = min(sf1, sf2)
            
            if op2 == '+':
                final_result = intermediate + num3
            else:
                final_result = intermediate - num3
                
            # For addition/subtraction, we need to match decimal places
            intermediate_str = format_with_sig_figs(intermediate, intermediate_sf)
            dp_intermediate = len(intermediate_str.split('.')[-1]) if '.' in intermediate_str else 0
            dp3 = len(problem['num3'].split('.')[-1]) if '.' in problem['num3'] else 0
            min_dp = min(dp_intermediate, dp3)
            
            formatted_result = f"{final_result:.{min_dp}f}"
            
        else:  # (op1 in ['+', '-']) and (op2 in ['×', '÷'])
            # First calculate num2 op2 num3, then num1 op1 result
            if op2 == '×':
                intermediate = num2 * num3
            else:
                intermediate = num2 / num3
                
            sf2 = count_sig_figs(problem['num2'])
            sf3 = count_sig_figs(problem['num3'])
            intermediate_sf = min(sf2, sf3)
            
            if op1 == '+':
                final_result = num1 + intermediate
            else:
                final_result = num1 - intermediate
                
            # For addition/subtraction, we need to match decimal places
            intermediate_str = format_with_sig_figs(intermediate, intermediate_sf)
            dp1 = len(problem['num1'].split('.')[-1]) if '.' in problem['num1'] else 0
            dp_intermediate = len(intermediate_str.split('.')[-1]) if '.' in intermediate_str else 0
            min_dp = min(dp1, dp_intermediate)
            
            formatted_result = f"{final_result:.{min_dp}f}"
        
        final_sf = count_sig_figs(formatted_result)
        
        return {
            'exact': final_result,
            'formatted': formatted_result,
            'sig_figs': final_sf
        }
    
    elif problem['operation'] == 'power':
        base = float(problem['base'])
        power = int(problem['power'])
        
        result = base ** power
        
        # In powers, the result has the same number of sig figs as the base
        base_sf = count_sig_figs(problem['base'])
        formatted_result = format_with_sig_figs(result, base_sf)
        
        return {
            'exact': result,
            'formatted': formatted_result,
            'required_sf': base_sf,
            'sig_figs': base_sf
        }
    
    elif problem['operation'] == 'sqrt':
        num = float(problem['num'])
        
        result = math.sqrt(num)
        
        # Square root has the same number of sig figs as the original number
        num_sf = count_sig_figs(problem['num'])
        formatted_result = format_with_sig_figs(result, num_sf)
        
        return {
            'exact': result,
            'formatted': formatted_result,
            'required_sf': num_sf,
            'sig_figs': num_sf
        }
        
    return None, None

def count_sig_figs(number_str):
    """Count significant figures following standard rules."""
    if isinstance(number_str, dict):
        # This is a calculation problem, not a simple number
        return None
        
    # Normalize input
    number_str = str(number_str).strip().lower()
    
    # Special case for zero
    if number_str == '0' or float(number_str) == 0:
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
        if not number_str:  # If it was all zeros
            return 1
        # Trailing zeros are not significant without a decimal
        return len(number_str.rstrip('0'))

def is_answer_numerically_correct(user_answer, exact_result, tolerance=1e-3):
    """Check if the user's answer is numerically correct within tolerance"""
    try:
        # Clean the user answer to handle various input formats
        user_answer = user_answer.strip().lower()
        
        # Remove commas and other formatting
        user_answer = user_answer.replace(',', '')
        
        # Try to convert to float
        user_value = float(user_answer)
        
        # For exact matches, don't use tolerance
        if user_answer == format_with_sig_figs(exact_result, count_sig_figs(user_answer)):
            return True
        
        # For very small numbers, use absolute tolerance
        if abs(exact_result) < 1e-10:
            return abs(user_value - exact_result) <= tolerance
        
        # Calculate relative error
        rel_error = abs((user_value - exact_result) / exact_result)
        
        return rel_error <= tolerance
    except:
        return False

def check_sig_figs_in_user_answer(user_answer, required_sig_figs):
    """Check if the user's answer has the correct number of significant figures"""
    try:
        # Clean and normalize the input
        user_answer = user_answer.strip().lower()
        user_answer = user_answer.replace(',', '')
        
        # Make sure it's a valid number before counting sig figs
        try:
            float(user_answer)
        except:
            return False
            
        user_sig_figs = count_sig_figs(user_answer)
        return user_sig_figs == required_sig_figs
    except:
        return False

def explain_sig_figs(problem, user_answer, result_info):
    """Explain why the user's answer is incorrect"""
    # For simple counting problems
    if not isinstance(problem, dict):
        correct_sig_figs = count_sig_figs(problem)
        user_sig_figs = int(user_answer) if user_answer.isdigit() else count_sig_figs(user_answer)
        
        if user_sig_figs == correct_sig_figs:
            return "Correct! Good job."
            
        explanation = ""
        number_str = problem
        
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
                if char == '0':  # Fixed: was 'digit' which is undefined
                    zero_count += 1
                else:
                    break
            if zero_count > 0:
                explanation += f"The {zero_count} zero(s) after the decimal point but before the first non-zero digit are NOT significant. "
        
        if number_str.replace('.', '').strip('0') == '':
            explanation += "For zero, we generally consider it to have 1 significant figure. "
        
        explanation += f"The correct answer is {correct_sig_figs} significant figures."
        
        return explanation
    
    # For calculation problems
    else:
        exact_result = result_info['exact']
        formatted_result = result_info['formatted']
        correct_sig_figs = result_info['sig_figs']
        
        # First check if the number is numerically close enough
        is_numerically_correct = is_answer_numerically_correct(user_answer, exact_result)
        
        # Then check if it has the right sig figs
        has_correct_sig_figs = check_sig_figs_in_user_answer(user_answer, correct_sig_figs)
        
        if is_numerically_correct and has_correct_sig_figs:
            return "Correct! Your calculated value and significant figures are both accurate."
            
        explanation = ""
        
        # Don't say the calculation is incorrect if it's actually correct
        if not is_numerically_correct:
            explanation += f"Your calculation appears to be incorrect. The expected result is approximately {formatted_result}. "
        elif not has_correct_sig_figs:
            # The calculation is correct but sig figs are wrong
            user_sig_figs = count_sig_figs(user_answer)
            explanation += f"Your calculation is numerically correct, but you have {user_sig_figs} significant figures when you should have {correct_sig_figs}. "
            
            operation = problem['operation']
            
            if operation == 'add_subtract':
                explanation += "For addition and subtraction, the result should have the same number of DECIMAL PLACES as the term with the fewest decimal places. "
                num1 = problem['num1']
                num2 = problem['num2']
                dp1 = len(num1.split('.')[-1]) if '.' in num1 else 0
                dp2 = len(num2.split('.')[-1]) if '.' in num2 else 0
                min_dp = min(dp1, dp2)
                explanation += f"In this problem, the first number has {dp1} decimal places and the second has {dp2}. The result should have {min_dp} decimal places. "
            
            elif operation == 'multiply_divide':
                explanation += "For multiplication and division, the result should have the same number of SIGNIFICANT FIGURES as the term with the fewest significant figures. "
                num1 = problem['num1']
                num2 = problem['num2']
                sf1 = count_sig_figs(num1)
                sf2 = count_sig_figs(num2)
                min_sf = min(sf1, sf2)
                explanation += f"In this problem, the first number has {sf1} significant figures and the second has {sf2}. The result should have {min_sf} significant figures. "
            
            elif operation == 'mixed':
                explanation += "For mixed operations, we need to apply the rules of significant figures sequentially based on the operations involved. "
                explanation += "First calculate using the order of operations (PEMDAS), then apply the appropriate sig fig rules at each step. "
                explanation += "For multiplication/division, limit to the fewest sig figs in the factors. For addition/subtraction, limit to the fewest decimal places. "
            
            elif operation == 'power':
                explanation += "When raising a number to a power, the result should have the same number of significant figures as the base number. "
                base = problem['base']
                base_sf = count_sig_figs(base)
                explanation += f"In this problem, the base has {base_sf} significant figures, so the result should also have {base_sf} significant figures. "
            
            elif operation == 'sqrt':
                explanation += "When taking a square root, the result should have the same number of significant figures as the original number. "
                num = problem['num']
                num_sf = count_sig_figs(num)
                explanation += f"In this problem, the number has {num_sf} significant figures, so the result should have {num_sf} significant figures. "
        
        if not is_numerically_correct or not has_correct_sig_figs:
            explanation += f"The correctly formatted answer is {formatted_result}."
        
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
        input, button {
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
        .mode-description {
            text-align: center;
            margin-bottom: 20px;
            font-style: italic;
            color: #666;
        }
        .calculation-result {
            font-size: 1.1rem;
            margin-top: 10px;
            text-align: center;
            color: #666;
        }
        .help-text {
            margin-top: 5px;
            font-size: 0.9rem;
            color: #666;
        }
        .rules-section {
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .rules-heading {
            font-weight: bold;
            margin-bottom: 10px;
        }
        .rules-list {
            margin-left: 20px;
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
                <span>Hard Mode (Calculations)</span>
            </div>
        </div>
        
        <div class="mode-description" id="mode-description">
            Simple Mode: Count the significant figures in numbers.
        </div>
        
        <div id="problem">
            <p id="problem-instruction">How many significant figures are in this number?</p>
            <div class="number-display" id="number">--</div>
            
            <div class="form-group">
                <label for="user-answer" id="answer-label">Your Answer:</label>
                <input type="number" id="user-answer" min="0" step="1">
                <div class="help-text" id="answer-help">Enter the number of significant figures.</div>
            </div>
            
            <button id="check-answer">Check Answer</button>
            <button id="new-problem">New Problem</button>
            
            <div id="result" class="result hidden"></div>
        </div>
        
        <div class="stats">
            <p>Score: <span id="correct-count">0</span> / <span id="total-count">0</span></p>
        </div>
        
        <div class="rules-section">
            <div class="rules-heading">Quick Reference: Significant Figures Rules</div>
            <ul class="rules-list">
                <li>All non-zero digits are significant (1, 2, 3, etc)</li>
                <li>Zeros between non-zero digits are significant (102 has 3 sig figs)</li>
                <li>Leading zeros are NEVER significant (0.00123 has 3 sig figs)</li>
                <li>Trailing zeros after a decimal point ARE significant (1.200 has 4 sig figs)</li>
                <li>Trailing zeros in a whole number are NOT significant unless indicated (1200 has 2 sig figs, but 1200. has 4)</li>
                <li>For addition/subtraction: result has same decimal places as term with fewest decimal places</li>
                <li>For multiplication/division: result has same significant figures as term with fewest sig figs</li>
            </ul>
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const numberDisplay = document.getElementById('number');
            const userAnswerInput = document.getElementById('user-answer');
            const answerLabel = document.getElementById('answer-label');
            const answerHelp = document.getElementById('answer-help');
            const checkAnswerButton = document.getElementById('check-answer');
            const newProblemButton = document.getElementById('new-problem');
            const resultDiv = document.getElementById('result');
            const hardModeCheckbox = document.getElementById('hard-mode');
            const correctCountSpan = document.getElementById('correct-count');
            const totalCountSpan = document.getElementById('total-count');
            const modeDescriptionDiv = document.getElementById('mode-description');
            const problemInstructionP = document.getElementById('problem-instruction');
            
            let currentProblem = '';
            let resultInfo = null;
            let correctCount = 0;
            let totalCount = 0;
            
            // Generate a new problem when the page loads
            generateNewProblem();
            
            // Event listener for the hard mode toggle
            hardModeCheckbox.addEventListener('change', function() {
                if (this.checked) {
                    modeDescriptionDiv.textContent = "Hard Mode: Calculate the result with the correct number of significant figures.";
                    problemInstructionP.textContent = "Calculate the following and report the answer with the correct significant figures:";
                    answerLabel.textContent = "Your Calculated Answer:";
                    answerHelp.textContent = "Enter your result using the correct significant figures.";
                    userAnswerInput.type = "text";  // Allow any input including scientific notation
                    userAnswerInput.step = "any";
                } else {
                    modeDescriptionDiv.textContent = "Simple Mode: Count the significant figures in numbers.";
                    problemInstructionP.textContent = "How many significant figures are in this number?";
                    answerLabel.textContent = "Your Answer:";
                    answerHelp.textContent = "Enter the number of significant figures.";
                    userAnswerInput.type = "number";
                    userAnswerInput.step = "1";
                }
                generateNewProblem();
            });
            
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
                    currentProblem = data.problem;
                    resultInfo = data.result_info;
                    
                    if (hardMode && typeof currentProblem === 'object') {
                        // This is a calculation problem
                        numberDisplay.textContent = currentProblem.problem;
                    } else {
                        // This is a simple number
                        numberDisplay.textContent = currentProblem;
                    }
                    
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
                const userAnswer = userAnswerInput.value.trim();
                
                if (!userAnswer) {
                    alert('Please enter an answer.');
                    return;
                }
                
                const isHardMode = hardModeCheckbox.checked;
                
                fetch('/check', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        problem: currentProblem,
                        user_answer: userAnswer,
                        hard_mode: isHardMode
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
    problem = generate_random_number(hard_mode)
    
    if isinstance(problem, dict):
        # This is a calculation problem
        result_info = calculate_result_and_sig_figs(problem)
        return jsonify({
            'problem': problem,
            'result_info': result_info
        })
    else:
        # This is a simple number
        correct_answer = count_sig_figs(problem)
        return jsonify({
            'problem': problem,
            'result_info': {'sig_figs': correct_answer}
        })

@app.route('/check', methods=['POST'])
def check():
    problem = request.json.get('problem')
    user_answer = request.json.get('user_answer')
    hard_mode = request.json.get('hard_mode', False)
    
    if isinstance(problem, dict):
        # This is a calculation problem
        result_info = calculate_result_and_sig_figs(problem)
        
        if hard_mode:
            # For hard mode with calculations, check both numerical accuracy and sig figs
            exact_result = result_info['exact']
            correct_sig_figs = result_info['sig_figs']
            
            numerically_correct = is_answer_numerically_correct(user_answer, exact_result)
            has_correct_sig_figs = check_sig_figs_in_user_answer(user_answer, correct_sig_figs)
            
            correct = numerically_correct and has_correct_sig_figs
        else:
            # Just check if they counted the sig figs correctly
            try:
                user_sig_figs = int(user_answer)
                correct = user_sig_figs == result_info['sig_figs']
            except:
                correct = False
                
        explanation = explain_sig_figs(problem, user_answer, result_info)
    else:
        # This is a simple number counting problem
        correct_answer = count_sig_figs(problem)
        
        if hard_mode:
            # They should have entered the calculated value
            correct = False  # This shouldn't happen in simple mode + hard mode
            explanation = "Error: Cannot use hard mode with simple problems."
        else:
            # They should have counted the sig figs
            try:
                user_answer_int = int(user_answer)
                correct = user_answer_int == correct_answer
            except:
                correct = False
                
            explanation = explain_sig_figs(problem, user_answer, {'sig_figs': correct_answer})
        
    return jsonify({
        'correct': correct,
        'explanation': explanation
    })

# For Vercel deployment
app = app
