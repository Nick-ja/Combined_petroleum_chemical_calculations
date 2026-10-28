import math
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView

# ================== Shared Components ==================
class InputField(MDBoxLayout):
    def __init__(self, hint_text, **kwargs):
        super().__init__(**kwargs)
        self.spacing = "20dp"
        self.size_hint_y = None
        self.height = "60dp"
        self.label = MDLabel(
            text=hint_text,
            halign="right",
            size_hint=(0.4, 1),
            theme_text_color="Secondary"
        )
        self.input = MDTextField(
            hint_text=f"Enter {hint_text}",
            mode="rectangle",
            size_hint=(0.6, None),
            height="50dp"
        )
        self.add_widget(self.label)
        self.add_widget(self.input)

class ResultScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll = ScrollView(size_hint=(1, 1))
        self.layout = MDGridLayout(
            cols=1,
            spacing="10dp",
            padding="20dp",
            size_hint_y=None,
            adaptive_height=True
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.scroll.add_widget(self.layout)
        self.add_widget(self.scroll)

    def show_results(self, results, back_screen):
        self.layout.clear_widgets()
        grid = MDGridLayout(
            cols=2,
            spacing="10dp",
            size_hint_y=None,
            adaptive_height=True,
            row_force_default=True,
            row_default_height="30dp"
        )
        for label, value in results.items():
            grid.add_widget(MDLabel(
                text=label + ":",
                halign="right",
                size_hint=(0.5, None),
                height="30dp"
            ))
            grid.add_widget(MDLabel(
                text=value,
                halign="left",
                size_hint=(0.5, None),
                height="30dp"
            ))
        self.layout.add_widget(grid)
        back_btn = MDRaisedButton(
            text="BACK",
            size_hint=(0.6, None),
            height="40dp",
            pos_hint={"center_x": 0.5}
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', back_screen))
        self.layout.add_widget(back_btn)

# ================== Petroleum Calculations ==================
def calc_vcf_pet(density, temp):
    dens = density * 1000
    if density < 0.771:
        var = (346.4228 / dens / dens) + (0.4388 / dens)
    elif density < 0.787:
        var = (2680.3206 / dens / dens) - 0.00336312
    elif density < 0.8385:
        var = 594.5418 / dens / dens
    else:
        var = (186.9696 / dens / dens) + (0.4862 / dens)
    vcf = round(math.exp(-var * (temp - 15) * (1 + 0.8 * var * (temp - 15))),5)
    return vcf

def calc_cbm_15_pet(l_act, vcf):
    return round((l_act * vcf)/1000,3)

def mt_vac(cbm_15, dens):
    return round(cbm_15 * dens,3)

def mt_air(cbm_15, dens):
    dens_air = dens - 0.0011
    return round(cbm_15 * dens_air,3)

def calc_cbm_20_pet(l_act, density):
    vcf_20C = calc_vcf_pet(density, 20)
    return round((l_act * vcf_20C)/1000,3)

def actual_barrels(cbm_act):
    return round(cbm_act * 6.28981077,2)

def calc_brrls(cbm_15, dens):
    vcf = calc_vcf_pet(dens, 15.5556)
    us_barrels = cbm_15 / (0.1589872949 * vcf)
    return round(us_barrels,2)

def calc_long_tons(mt_air):
    return round(mt_air * 0.9842065,3)

def calc_gallons(brrls):
    return round(brrls * 42,2)

def calc_api(dens, temp):
    vcf = calc_vcf_pet(dens, 15.5556)
    api = (141.5 / ((((dens * 1000) * vcf)) / 999.016)) - 131.5
    return round(api,1)

class PetroleumInputScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDGridLayout(
            cols=1,
            spacing="20dp",
            padding="40dp",
            adaptive_height=True
        )
        self.inputs = {
            "density": InputField("Density in Vac in format 'x.xxxx'"),
            "temp": InputField("Temperature (°C)"),
            "wanted_liters_actual": InputField("Actual liters"),
        }
        for field in self.inputs.values():
            layout.add_widget(field)
        
        btn_layout = MDBoxLayout(spacing="20dp", size_hint=(1, None), height="60dp")
        self.calc_btn = MDRaisedButton(text="CALCULATE", size_hint=(0.5, None), height="50dp")
        self.back_btn = MDRaisedButton(text="BACK TO START", size_hint=(0.5, None), height="50dp")
        
        btn_layout.add_widget(self.back_btn)
        btn_layout.add_widget(self.calc_btn)
        layout.add_widget(btn_layout)
        self.add_widget(layout)

# ================== Chemical Calculations ==================
def calc_wanted_dens(dens, entered_temp, dcc, wanted_temp):
    wanted_dens = ((entered_temp - wanted_temp) * dcc) + dens
    return round(wanted_dens, 4)

def dens_15_air(entered_temp, dcc, dens_air):
    dens_air_15 = ((entered_temp - 15) * dcc) + dens_air
    return round(dens_air_15, 4)

def calc_dens_vac(dens_air):
    dens_vac_15 = dens_air + 0.0011
    return round(dens_vac_15, 4)

def dens_20_air(entered_temp, dcc, dens_air):
    dens_air_20 = ((entered_temp - 20) * dcc) + dens_air
    return round(dens_air_20, 4)

def calc_dens_actual(dens, entered_temp, dcc, actual_temp):
    dens_actual = ((entered_temp - actual_temp) * dcc) + dens
    return round(dens_actual, 4)

def calc_cbm_actual(mt_air, dens_actual):
    cbm_actual = mt_air / dens_actual
    return round(cbm_actual, 3)

def calc_cbm_15(mt_air, dens):
    cbm_15 = mt_air / dens
    return round(cbm_15, 3)

def calc_cbm_20(mt_air, dens_20):
    return round(mt_air / dens_20, 3)

def calc_mt_vac(cbm_15, dens_vac):
    return round(cbm_15 * dens_vac, 3)

def us_barrels(mt_vac, dens_vac, dcc):
    us_brrls = (mt_vac / (dens_vac - (0.5556 * dcc))) / 0.1589872949
    return round(us_brrls, 2)

def calc_long_tons(mt_air):
    return round(mt_air * 0.9842065, 3)

def us_gallons(barrels):
    return round(barrels * 42, 2)

class ChemicalInputScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDGridLayout(
            cols=1,
            spacing="20dp",
            padding="40dp",
            adaptive_height=True
        )
        self.inputs = {
            "dens_air": InputField("Density in air"),
            "dens_temp": InputField("Density temperature (°C)"),
            "dcc": InputField("DCC"),
            "wanted_temp": InputField("Wanted temperature (°C)"),
            "actual_temp": InputField("Actual temperature (°C)"),
            "mt_air": InputField("MT Air")
        }
        for field in self.inputs.values():
            layout.add_widget(field)
        
        btn_layout = MDBoxLayout(spacing="20dp", size_hint=(1, None), height="60dp")
        self.calc_btn = MDRaisedButton(text="CALCULATE", size_hint=(0.5, None), height="50dp")
        self.back_btn = MDRaisedButton(text="BACK TO START", size_hint=(0.5, None), height="50dp")
        
        btn_layout.add_widget(self.back_btn)
        btn_layout.add_widget(self.calc_btn)
        layout.add_widget(btn_layout)
        self.add_widget(layout)

# ================== Start Screen ==================
class StartScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = MDBoxLayout(orientation='vertical')
        
        # Create a grid layout for buttons that takes half the screen
        button_layout = MDGridLayout(
            cols=1,
            padding=40,
            spacing=30,
            size_hint=(1, 0.8),  # Takes 50% of vertical space
            pos_hint={"center_x": 0.5}
        )

        # Create buttons with larger dimensions
        btn1 = MDRaisedButton(
            text="Petroleum Calculations",
            size_hint=(1, None),
            height="100dp",  # Increased height
            font_size="22sp"  # Larger font
        )
        
        btn2 = MDRaisedButton(
            text="Chemical Calculations",
            size_hint=(1, None),
            height="100dp",  # Increased height
            font_size="22sp"  # Larger font
        )

        # Create copyright label with larger text
        copyright_label = MDLabel(
            text="© Nick Jacobs",
            halign="center",
            theme_text_color="Custom",
            text_color="#00FF00",
            font_style="H6",  # Larger font style
            size_hint=(1, 0.3)  # Takes 10% of vertical space
        )

        btn1.bind(on_release=lambda x: setattr(self.manager, 'current', "petroleum_input"))
        btn2.bind(on_release=lambda x: setattr(self.manager, 'current', "chemical_input"))
        
        button_layout.add_widget(btn1)
        button_layout.add_widget(btn2)
        
        main_layout.add_widget(button_layout)
        main_layout.add_widget(copyright_label)
        self.add_widget(main_layout)

class Calculations_Nick_JacobsApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        
        self.sm = MDScreenManager()
        
        # Create and add all screens
        self.sm.add_widget(StartScreen(name="start"))
        self.sm.add_widget(PetroleumInputScreen(name="petroleum_input"))
        self.sm.add_widget(ResultScreen(name="petroleum_result"))
        self.sm.add_widget(ChemicalInputScreen(name="chemical_input"))
        self.sm.add_widget(ResultScreen(name="chemical_result"))
        
        # Set up button bindings
        petroleum_input = self.sm.get_screen("petroleum_input")
        chemical_input = self.sm.get_screen("chemical_input")
        
        petroleum_input.calc_btn.bind(on_release=self.petroleum_calculate)
        petroleum_input.back_btn.bind(on_release=lambda x: setattr(self.sm, 'current', "start"))
        chemical_input.calc_btn.bind(on_release=self.chemical_calculate)
        chemical_input.back_btn.bind(on_release=lambda x: setattr(self.sm, 'current', "start"))
        
        return self.sm

    # Petroleum Calculations
    def petroleum_validate_inputs(self):
        values = {}
        screen = self.sm.get_screen("petroleum_input")
        for key, field in screen.inputs.items():
            try:
                values[key] = float(field.input.text)
            except ValueError:
                field.input.error = True
                return None
        return values

    def petroleum_calculate(self, *args):
        inputs = self.petroleum_validate_inputs()
        if not inputs: return

        dv = inputs['density']
        tp = inputs['temp']
        al = inputs['wanted_liters_actual']

        density_air = dv - 0.0011
        degrees_farenheit = round((tp * 1.8) + 32, 1)
        calculated_api_gravity = calc_api(dv, tp)
        calculated_vcf = calc_vcf_pet(dv, tp)
        calculated_cbm_act = round(al / 1000, 3)
        calculated_cbm_15 = calc_cbm_15_pet(al, calculated_vcf)
        calculated_cbm_20 = calc_cbm_20_pet(al, dv)
        calculated_mt_vac = mt_vac(calculated_cbm_15, dv)
        calculated_mt_air = mt_air(calculated_cbm_15, dv)
        calculated_act_barrels = actual_barrels(calculated_cbm_act)
        calculated_us_barrels = calc_brrls(calculated_cbm_15, dv)
        calculated_long_tons = calc_long_tons(calculated_mt_air)
        calculated_us_gallons = calc_gallons(calculated_us_barrels)

        results = {
            "Density 15°C Vac": f"{dv:,.4f}",
            "Density at 15°C Air": f"{density_air:,.4f}",
            "API Gravity at 60°F": f"{calculated_api_gravity:,.1f}°",
            "Temperature in Celsius": f"{tp:,.2f}°C",
            "Temperature in Farenheit": f"{degrees_farenheit:,.1f}°F",
            "VCF": f"{calculated_vcf:,.5f}",
            "Cbm actual": f"{calculated_cbm_act:,.3f}",
            "Cbm at 15°C": f"{calculated_cbm_15:,.3f}",
            "Cbm at 20°C": f"{calculated_cbm_20:,.3f}",
            "MT Vac": f"{calculated_mt_vac:,.3f}",
            "MT Air": f"{calculated_mt_air:,.3f}",
            "Long Tons (air)": f"{calculated_long_tons:,.3f}",
            "Actual US Barrels": f"{calculated_act_barrels:,.2f}",
            "US Barrels at 60°F": f"{calculated_us_barrels:,.2f}",
            "US Gallons at 60°F": f"{calculated_us_gallons:,.2f}"
        }

        self.sm.get_screen("petroleum_result").show_results(results, "petroleum_input")
        self.sm.current = "petroleum_result"

    # Chemical Calculations
    def chemical_validate_inputs(self):
        values = {}
        screen = self.sm.get_screen("chemical_input")
        for key, field in screen.inputs.items():
            try:
                values[key] = float(field.input.text)
            except ValueError:
                field.input.error = True
                return None
        return values

    def chemical_calculate(self, *args):
        inputs = self.chemical_validate_inputs()
        if not inputs: return

        da = inputs['dens_air']
        dt = inputs['dens_temp']
        dcc = inputs['dcc']
        wt = inputs['wanted_temp']
        at = inputs['actual_temp']
        mt = inputs['mt_air']

        calc_dens = calc_wanted_dens(da, dt, dcc, wt)
        dens_15_air_val = dens_15_air(dt, dcc, da)
        dens_15_vac_val = calc_dens_vac(dens_15_air_val)
        dens_20_air_val = dens_20_air(dt, dcc, da)
        dens_actual_val = calc_dens_actual(da, dt, dcc, at)
        cbm_actual_val = calc_cbm_actual(mt, dens_actual_val)
        cbm_15_val = calc_cbm_15(mt, dens_15_air_val)
        cbm_20_val = calc_cbm_20(mt, dens_20_air_val)
        mt_vac_val = calc_mt_vac(cbm_15_val, dens_15_vac_val)
        us_barrels_val = us_barrels(mt_vac_val, dens_15_vac_val, dcc)
        long_tons_val = calc_long_tons(mt)
        us_gallons_val = us_gallons(us_barrels_val)

        results = {
            f"Density at {wt}°C air": f"{calc_dens:.4f}",
            "Density at 15°C air": f"{dens_15_air_val:.4f}",
            "Density at 15°C vac": f"{dens_15_vac_val:.4f}",
            "Density at 20°C air": f"{dens_20_air_val:.4f}",
            f"Density at {at}°C air": f"{dens_actual_val:.4f}",
            f"Cbm at {at}°C": f"{cbm_actual_val:,.3f}",
            "Cbm at 15°C": f"{cbm_15_val:,.3f}",
            "Cbm at 20°C": f"{cbm_20_val:,.3f}",
            "MT Vac": f"{mt_vac_val:,.3f}",
            "US Barrels at 60°F": f"{us_barrels_val:,.2f}",
            "Long Tons (air)": f"{long_tons_val:,.3f}",
            "US Gallons at 60°F": f"{us_gallons_val:,.2f}"
        }

        self.sm.get_screen("chemical_result").show_results(results, "chemical_input")
        self.sm.current = "chemical_result"

if __name__ == "__main__":
    Calculations_Nick_JacobsApp().run()