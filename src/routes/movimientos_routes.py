from flask import blueprints, render_template, redirect, url_for
from controlers.movementcontroler import all_movements, rev_movement

movements_bp = blueprints('movimientos', __name__)

@movements_bp.route('/movements')
def movements():
    return render_template('movements.html', movimientos = all_movements())

@movements_bp.route('/revert_movement/<int:movement_id>', methods=['POST'])
def revert_movement(movement_id):
    rev_movement(movement_id)
    return redirect(url_for('movements'))
