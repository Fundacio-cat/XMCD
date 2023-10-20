import argparse

parser = argparse.ArgumentParser(description='Rep quin navegador i cercador utilitzarà per paràmetre')
parser.add_argument('navegador', type=str, help='Quin navegador? Chrome / Firefox')
parser.add_argument('cercador',  type=str, help='Quin cercador? Google / Bing')

args = parser.parse_args()

print('Navegador:', args.navegador)
print('Cercador:', args.cercador)

