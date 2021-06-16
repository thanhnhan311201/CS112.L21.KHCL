import unittest
import random
from TaoBien import Modulo_Fibonacci

class Gen_Test(unittest.TestCase):
    def test_1_manual(self):
        with open("input/Tao_1.in", 'a+') as f_in:        
            with open("output/Tao_1.out", 'a+') as f_out:    
                self.assertEqual(Modulo_Fibonacci(3,2), 15)        
                f_in.write('1 1')                   
                f_out.write('{}'.format(Modulo_Fibonacci(1,1)))

    def test_2_manual(self):
        with open("input/Tao_2.in", 'a+') as f_in:        
            with open("output/Tao_2.out", 'a+') as f_out:    
                self.assertEqual(Modulo_Fibonacci(3,2), 15)        
                f_in.write('1000 100000')                   
                f_out.write('{}'.format(Modulo_Fibonacci(1000,100000)))

    def test_auto(self):
        for i in range(3,101):
            index_ = "input/Tao_%d.in" % i
            index = "output/Tao_%d.out" % i
            with open(index_, 'a+') as f_in:
                with open(index, 'a+') as f_out:
                    n = random.randint(2, 999)
                    k = random.randint(2,99999)
                    self.assertEqual(Modulo_Fibonacci(3, 2), 15)
                    f_in.write('{} {}'.format(n, k))
                    f_out.write('{}'.format(Modulo_Fibonacci(n, k)))

if __name__ == "__main__":
    unittest.main()