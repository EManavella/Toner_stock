from flask import blueprints, render_template, redirect, url_for, request, flash
from controlers.sectorcontroler import all_sectors, del_sector, add_sector
from controlers.validationcontroler import validar_entrada_sector

sector_bp = blueprints('sectores', __name__)

@sector_bp.route('/sectores')
def sectores():
    return render_template('sectores.html', sectores = all_sectors())

@sector_bp.route('/delete_sector/<int:sector_id>', methods=['POST'])
def delete_sector(sector_id):
    del_sector(sector_id)
    return redirect(url_for('sectores'))

@sector_bp.route('/alta_sector', methods=['POST'])
def alta_sector():
    if request.method == 'POST':
        insumo_nombre = request.form.get('insumo_nombre', type= str)
        duracion_predefinida = request.form.get('duracion_predefinida', type= int)

        if validar_entrada_sector(insumo_nombre, duracion_predefinida):
            if add_sector(insumo_nombre, duracion_predefinida):
                flash('Sector registrado exitosamente.', 'success')
                return redirect(url_for('sectores'))   
            else:
                flash(f'Error al registrar el sector', 'danger')
        
        return redirect(url_for('sectores'))
