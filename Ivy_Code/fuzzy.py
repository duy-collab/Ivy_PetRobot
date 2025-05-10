from skfuzzy import control as ctrl
import pickle
import time

class Fuzzy():
    def __init__(self):
        self.goar_model = self.load_model("/home/pi/Ivy/src/fuzzy/Izzy_goar.pkl")
        self.foll_model = self.load_model("/home/pi/Ivy/src/fuzzy/Izzy_foll.pkl")
        
        
    def load_model(self, model_path):
        with open(model_path, 'rb') as file:
            control = pickle.load(file)
        simulation = ctrl.ControlSystemSimulation(control)

        return simulation

    def go_around(self, LL = 0.0, FF = 0.0, RR = 0.0):
        self.goar_model.input['L'] = LL
        self.goar_model.input['F'] = FF
        self.goar_model.input['R'] = RR
        
        self.goar_model.compute()
        v = self.goar_model.output['v']
        w = self.goar_model.output['w']
        
        return v, w
    
    def follow(self, EE = 0.0, WW = 0.0):
        self.foll_model.input['E'] = EE
        self.foll_model.input['W'] = WW
        
        self.foll_model.compute()
        v = self.foll_model.output['v']
        w = self.foll_model.output['w']
        
        return v, w
        
    def compute(self, LL=0.0, FF=0.0, RR=0.0, EE=0.0, WW=0.0):
        v_goar, w_goar = self.go_around(LL, FF, RR)
        v_foll, w_foll = self.follow(EE, WW)

        return {
            "go_around": {"v": v_goar, "w": w_goar},
            "follow": {"v": v_foll, "w": w_foll}
        }
if __name__ == "__main__":
    fuzzy = Fuzzy()
    fuzzy.compute(LL = 1.5, FF = 0.5, RR = 1.5, EE = -5.0, WW = 150)
