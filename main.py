import random
import time
from collections import deque

DEFAULT_BALANCE = 1000
SYMBOL_ANIMATION_DELAY = 0.3

SYMBOLS = {
    'A': {'count': 2, 'value': 5},
    'B': {'count': 4, 'value': 4},
    'C': {'count': 6, 'value': 3},
    'D': {'count': 8, 'value': 2},
    '7': {'count': 1, 'value': 10}
}

class Player:
    def __init__(self):
        self.balance = DEFAULT_BALANCE
        self.level = 1
        self.xp = 0
        self.jackpots = 0
    
    def add_xp(self, amount):
        self.xp += amount
        if self.xp >= self.level * 100:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.xp = 0
        print(f"\n⭐ Nível UP! Agora você é nível {self.level} ⭐")
        self.balance += self.level * 50

class SlotMachine:
    def __init__(self):
        self.config = {
            'ROWS': 3,
            'COLS': 3,
            'MAX_LINES': 3,
            'MIN_BET': 1,
            'MAX_BET': 100,
            'SYMBOLS': SYMBOLS
        }
        self.history = deque(maxlen=10)
        self.player = Player()
    
    def get_valid_input(self, prompt, input_type=int, min_val=None, max_val=None):
        while True:
            try:
                value = input_type(input(prompt))
                if min_val is not None and value < min_val:
                    print(f"Valor mínimo permitido: {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"Valor máximo permitido: {max_val}")
                    continue
                return value
            except ValueError:
                print(f"Por favor, insira um {input_type.__name__} válido.")
    
    def generate_spin(self):
        all_symbols = []
        for symbol, data in self.config['SYMBOLS'].items():
            all_symbols.extend([symbol] * data['count'])
        
        columns = []
        for _ in range(self.config['COLS']):
            column = []
            current_symbols = all_symbols.copy()
            for _ in range(self.config['ROWS']):
                value = random.choice(current_symbols)
                current_symbols.remove(value)
                column.append(value)
            columns.append(column)
        return columns
    
    def animate_spin(self, final_columns):
        symbols = [s for s, data in self.config['SYMBOLS'].items() for _ in range(data['count'])]
        for _ in range(10):
            for col in range(self.config['COLS']):
                temp_columns = final_columns.copy()
                temp_columns[col] = [random.choice(symbols) for _ in range(self.config['ROWS'])]
                self.print_slot_machine(temp_columns)
                time.sleep(SYMBOL_ANIMATION_DELAY)
    
    def print_slot_machine(self, columns):
        print("\n" + "-" * 20)
        for row in range(self.config['ROWS']):
            print(" | ".join(column[row] for column in columns))
        print("-" * 20 + "\n")
    
    def check_winnings(self, columns, lines, bet):
        winnings = 0
        winning_lines = []
        
        for line in range(lines):
            first_symbol = columns[0][line]
            if all(column[line] == first_symbol for column in columns):
                multiplier = self.config['SYMBOLS'][first_symbol]['value']
                winnings += bet * multiplier
                winning_lines.append(line + 1)
                
                if len(set(column[line] for column in columns)) == 1:
                    winnings += bet * (multiplier * 0.5)
        
        return winnings, winning_lines
    
    def play_round(self):
        print(f"\nSaldo atual: ${self.player.balance}")
        lines = self.get_valid_input(
            f"Quantas linhas quer apostar (1-{self.config['MAX_LINES']})? ",
            min_val=1, max_val=self.config['MAX_LINES']
        )
        
        while True:
            bet = self.get_valid_input(
                f"Quanto quer apostar em cada linha (${self.config['MIN_BET']}-${self.config['MAX_BET']})? $",
                min_val=self.config['MIN_BET'], max_val=self.config['MAX_BET']
            )
            total_bet = bet * lines
            
            if total_bet > self.player.balance:
                print(f"Saldo insuficiente. Seu saldo: ${self.player.balance}")
            else:
                break
        
        self.player.balance -= total_bet
        print(f"Aposta total: ${total_bet} em {lines} linhas")
        
        input("Pressione Enter para girar...")
        final_columns = self.generate_spin()
        self.animate_spin(final_columns)
        self.print_slot_machine(final_columns)
        
        winnings, winning_lines = self.check_winnings(final_columns, lines, bet)
        self.player.balance += winnings
        self.player.add_xp(total_bet // 10)
        
        if winnings > 0:
            print(f"Você ganhou ${winnings}!")
            if winning_lines:
                print(f"Linhas vencedoras: {', '.join(map(str, winning_lines))}")
        else:
            print("Não houve ganhos desta vez.")
        
        self.history.append((final_columns, winnings))
    
    def show_rules(self):
        print("\nREGRAS E PAGAMENTOS:")
        print(f"Linhas: 1-{self.config['MAX_LINES']}, Aposta: ${self.config['MIN_BET']}-${self.config['MAX_BET']} por linha")
        print("\nMULTIPLICADORES:")
        for symbol, data in sorted(self.config['SYMBOLS'].items(), key=lambda x: -x[1]['value']):
            print(f"{symbol}: {data['value']}x")
        print("\nBÔNUS: Linha completa +50% do multiplicador")
        input("\nPressione Enter para voltar...")
    
    def show_history(self):
        print("\nÚLTIMOS RESULTADOS:")
        for i, (columns, win) in enumerate(reversed(self.history), 1):
            print(f"\nJogada {i}: Ganhos: ${win}")
            self.print_slot_machine(columns)
        input("\nPressione Enter para voltar...")
    
    def show_menu(self):
        while True:
            print("\n" + "="*40)
            print(f" SALDO: ${self.player.balance} | NÍVEL: {self.player.level} | XP: {self.player.xp}/{self.player.level*100}")
            print("="*40)
            print("1. Jogar")
            print("2. Regras e Pagamentos")
            print("3. Histórico")
            print("4. Sair")
            
            choice = self.get_valid_input("Escolha: ", min_val=1, max_val=4)
            
            if choice == 1:
                self.play_round()
            elif choice == 2:
                self.show_rules()
            elif choice == 3:
                self.show_history()
            else:
                print(f"\nFim do jogo! Saldo final: ${self.player.balance}")
                return
    
    def start(self):
        print("=== SLOT MACHINE PREMIUM ===")
        self.show_menu()

if __name__ == "__main__":
    machine = SlotMachine()
    machine.start()