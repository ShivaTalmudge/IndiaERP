from decimal import Decimal

def _decimal(value, default="0"):
    """Helper to safely convert values to Decimal."""
    try:
        return Decimal(str(value)) if value else Decimal(default)
    except Exception:
        return Decimal(default)

def number_to_words(amount):
    """Convert decimal amount to Indian words (for invoice)."""
    ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven',
            'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen',
            'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
    tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty',
            'Sixty', 'Seventy', 'Eighty', 'Ninety']

    def two_digits(n):
        if n < 20:
            return ones[n]
        return tens[n // 10] + (' ' + ones[n % 10] if n % 10 else '')

    def three_digits(n):
        if n >= 100:
            if n // 100 < len(ones):
                return ones[n // 100] + ' Hundred' + (' ' + two_digits(n % 100) if n % 100 else '')
            else:
                return str(n // 100) + ' Hundred' + (' ' + two_digits(n % 100) if n % 100 else '')
        return two_digits(n)

    if amount is None:
        return 'Zero'
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return 'Zero'

    n = int(amount)
    if n == 0:
        return 'Zero'
    
    parts = []
    
    # Crore
    crore = n // 10000000
    if crore:
        parts.append(three_digits(crore) + ' Crore')
    n %= 10000000
    
    # Lakh
    lakh = n // 100000
    if lakh:
        parts.append(three_digits(lakh) + ' Lakh')
    n %= 100000
    
    # Thousand
    thousand = n // 1000
    if thousand:
        parts.append(three_digits(thousand) + ' Thousand')
    n %= 1000
    
    # Hundreds and below
    if n:
        parts.append(three_digits(n))
        
    return ' '.join(parts) + ' Only'
