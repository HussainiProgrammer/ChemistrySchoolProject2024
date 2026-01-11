class ScientificNotation:
    def __init__(self, coefficient: int|float, exponent: int):
        self.coefficient = coefficient
        self.exponent = exponent

    def __mul__(self, multiplier):
        if type(multiplier) == ScientificNotation:
            product = ScientificNotation(self.coefficient * multiplier.coefficient, self.exponent + multiplier.exponent)

        else:
            product = ScientificNotation(self.coefficient * multiplier, self.exponent)

        return product

    def __rmul__(self, multiplicand):
        if type(multiplicand) == ScientificNotation:
            product = ScientificNotation(multiplicand.coefficient * self.coefficient, multiplicand.exponent + self.exponent)

        else:
            product = ScientificNotation(multiplicand * self.coefficient, self.exponent)

        return product
    
    def __truediv__(self, divisor):
        if type(divisor) == ScientificNotation:
            quotient = ScientificNotation(self.coefficient / divisor.coefficient, self.exponent - divisor.exponent)

        else:
            quotient = ScientificNotation(self.coefficient / divisor, self.exponent)

        return quotient

    def __rtruediv__(self, dividend):
        if type(dividend) == ScientificNotation:
            quotient = ScientificNotation(dividend.coefficient / self.coefficient, dividend.exponent - self.exponent)

        else:
            quotient = ScientificNotation(dividend / self.coefficient, -self.exponent)

        return quotient
    
    def __repr__(self) -> str:
        return f"{self.coefficient} * 10**{self.exponent}"

    def LaTeX(self) -> str:
        return str(self.coefficient) + " \\times 10^{"+ str(self.exponent) + "}"
    
    def evaluate(self):
        return self.coefficient * 10**self.exponent

if __name__ == "__main__":
    AVOGADROS_NUMBER = ScientificNotation(6.023, 23)
    print(AVOGADROS_NUMBER)
    print(f"Avogradro's Number, symbolized as Nₐ, is estimated to be {AVOGADROS_NUMBER}")

    numberOfParticles = ScientificNotation(3.0115, 35)
    print(numberOfParticles)

    numberOfMoles = numberOfParticles / AVOGADROS_NUMBER
    print(numberOfMoles)