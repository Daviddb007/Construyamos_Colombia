"""initial migration

Revision ID: 6ee3994227d4
Revises: 
Create Date: 2026-06-30 21:12:30.575801

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ee3994227d4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create sectores table
    op.create_table(
        'sectores',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(100), nullable=False, unique=True),
        sa.Column('icono', sa.String(50), nullable=True),
        sa.Column('activo', sa.Boolean(), default=True),
    )

    # Create participaciones table
    op.create_table(
        'participaciones',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('departamento', sa.String(100), nullable=True),
        sa.Column('municipio', sa.String(100), nullable=True),
        sa.Column('rango_edad', sa.String(50), nullable=True),
        sa.Column('genero', sa.String(50), nullable=True),
        sa.Column('sector_prioritario_id', sa.Integer(), sa.ForeignKey('sectores.id'), nullable=True),
        sa.Column('problema_principal', sa.String(200), nullable=True),
        sa.Column('problema_otro', sa.Text(), nullable=True),
        sa.Column('propuesta', sa.Text(), nullable=False),
        sa.Column('ip_hash', sa.String(64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_participaciones_created_at', 'participaciones', ['created_at'])
    op.create_index('ix_participaciones_departamento', 'participaciones', ['departamento'])
    op.create_index('ix_participaciones_sector_prioritario_id', 'participaciones', ['sector_prioritario_id'])

    # Create participacion_sectores association table
    op.create_table(
        'participacion_sectores',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('participacion_id', sa.Integer(), sa.ForeignKey('participaciones.id'), nullable=True),
        sa.Column('sector_id', sa.Integer(), sa.ForeignKey('sectores.id'), nullable=True),
    )

    # Create catalogo_problemas table
    op.create_table(
        'catalogo_problemas',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('sector_id', sa.Integer(), sa.ForeignKey('sectores.id'), nullable=False),
        sa.Column('nombre', sa.String(200), nullable=False),
        sa.Column('activo', sa.Boolean(), default=True),
    )


def downgrade():
    op.drop_table('catalogo_problemas')
    op.drop_table('participacion_sectores')
    op.drop_index('ix_participaciones_sector_prioritario_id', table_name='participaciones')
    op.drop_index('ix_participaciones_departamento', table_name='participaciones')
    op.drop_index('ix_participaciones_created_at', table_name='participaciones')
    op.drop_table('participaciones')
    op.drop_table('sectores')
