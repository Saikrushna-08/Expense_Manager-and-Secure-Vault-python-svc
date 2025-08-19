# views.py

from flask import jsonify

def format_expenses_list(expenses):
    """Formats a list of expenses into a readable string."""
    if not expenses:
        return 'No expenses found.\n'

    output = '--- All Expenses ---\n'
    for expense in expenses:
        output += f'_id: {expense["_id"]}, Category: {expense["category"]}, Amount: {expense["amount"]:.2f}, Date: {expense["date"]}\n'
    return output

def format_single_expense(expense):
    """Formats a single expense into a readable string."""
    return f'--- Expense Details ---\n_id: {expense["_id"]}, Category: {expense["category"]}, Amount: {expense["amount"]:.2f}, Date: {expense["date"]}\n'

def format_total_expenses(total):
    """Formats the total expenses into a readable string."""
    return f'\n--- Total Expenses: {total:.2f} ---\n'

def format_response(message, status, code=200):
    """
    Formats a Flask response.

    Args:
        message (str or dict): The message to return to the user.
        status (str): The status of the operation (e.g., 'success', 'error', 'info').
        code (int): The HTTP status code.

    Returns:
        A Flask response object.
    """
    response = {
        'status': status,
        'message': message
    }
    return jsonify(response), code