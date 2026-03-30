from flask import Flask, render_template, request
import vgamepad as vg

app = Flask(__name__)

print("========================================")
print("      CUSTOM RACING GAMEPAD SERVER      ")
print("========================================")
print("Server running! Connect phones to your IP at port 5000.")
print("Controllers will automatically connect when a player presses a button.")

# Dictionary to hold the gamepads, starts completely empty!
gamepads = {}

def get_gamepad(player_id):
    # If this player hasn't pressed a button yet, create their controller instantly
    if player_id not in gamepads:
        if len(gamepads) < 4:
            print(f" -> Player {player_id} connected! Plugging in virtual controller...")
            gamepads[player_id] = vg.VX360Gamepad()
    return gamepads.get(player_id)

BUTTON_MAP = {
    'A': vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    'B': vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    'X': vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    'Y': vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    'LB': vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
    'RB': vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    'BACK': vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
    'START': vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
    'GUIDE': vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE,
    'LS_CLICK': vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
    'RS_CLICK': vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
    'UP': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
    'DOWN': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
    'LEFT': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
    'RIGHT': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/action', methods=['POST'])
def action():
    data = request.json
    player_id = data.get('player', 1)
    
    # Grab the controller for this player (or create it if it's their first input)
    gp = get_gamepad(player_id)
    if not gp:
        return "OK", 200

    # Handle Tilt Steering
    if 'analog_steer' in data:
        val = int(data['analog_steer'] * 32767)
        val = max(-32768, min(32767, val)) 
        gp.left_joystick(x_value=val, y_value=0)
        gp.update()
        return "OK", 200

    # Handle Standard Buttons
    btn = data.get('button')
    state = data.get('state') 

    if btn in BUTTON_MAP:
        if state == 'press':
            gp.press_button(button=BUTTON_MAP[btn])
        else:
            gp.release_button(button=BUTTON_MAP[btn])
    elif btn == 'LT':
        gp.left_trigger(value=255 if state == 'press' else 0)
    elif btn == 'RT':
        gp.right_trigger(value=255 if state == 'press' else 0)
    elif btn == 'STEER_LEFT':
        gp.left_joystick(x_value=-32768 if state == 'press' else 0, y_value=0)
    elif btn == 'STEER_RIGHT':
        gp.left_joystick(x_value=32767 if state == 'press' else 0, y_value=0)

    gp.update()
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)