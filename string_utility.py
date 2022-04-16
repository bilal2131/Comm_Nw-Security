

import string
import random
#list of characters to consider for random string generation
char_list = string.ascii_letters + string.digits
N=16
def random_string():
  str1 = ''.join(random.choices(char_list,k=N))
  return str1

if __name__=='__main__':
  print(random_string())
  
