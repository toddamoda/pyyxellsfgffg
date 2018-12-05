"""Badge creator."""
import argparse
import subprocess


def badges():
    """Create badges."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-cov', '--coverage', type=float, default=None, help='Test coverage percent')
    opts = parser.parse_args()

    if opts.coverage:
        if 0. <= opts.coverage < 20.:
            colour = 'red'
        elif 20. <= opts.coverage < 40.:
            colour = 'orange'
        elif 40. <= opts.coverage < 60.:
            colour = 'yellow'
        elif 60. <= opts.coverage < 80.:
            colour = 'yellowgreen'
        elif 80. <= opts.coverage < 90.:
            colour = 'green'
        elif 90. <= opts.coverage <= 100.:
            colour = 'brightgreen'
        else:
            colour = 'lightgrey'
        percent = '{:.2f}'.format(opts.coverage)
        process = 'wget -O coverage.svg https://img.shields.io/badge/coverage-' + percent + '%25-' + colour + '.svg'
        subprocess.run(process, shell=True)


if __name__ == '__main__':
    badges()
