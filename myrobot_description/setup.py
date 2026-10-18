from glob import glob

from setuptools import find_packages, setup

package_name = 'myrobot_description'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/urdf', glob('urdf/*')),
        ('share/' + package_name + '/launch', glob('launch/*')),
        ('share/' + package_name + '/worlds', glob('worlds/*')),
        ('share/' + package_name + '/config', glob('config/*')),
        ('share/' + package_name + '/maps', glob('maps/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Chaabene Jasser',
    maintainer_email='Jasser.chaabane@eniso.u-sousse.tn',
    description=(
        'Autonomous Mobile Robot (AMR) simulation package with 6-wheel '
        'differential drive, SLAM Toolbox mapping, and Nav2 navigation '
        'in Gazebo and RViz2.'
    ),
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
