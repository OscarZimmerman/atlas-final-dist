import uproot
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from lmfit.models import PolynomialModel, GaussianModel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Default parameters
tuple_path = "https://atlas-opendata.web.cern.ch/atlas-opendata/samples/2020/GamGam/Data/"
lumi = 10  # fb-1
fraction = 0.8  # Reduce this if you want the code to run quicker

# Photon data processing functions
def calc_myy(photon_pt, photon_eta, photon_phi, photon_E):
    px_0 = photon_pt[0] * math.cos(photon_phi[0])
    py_0 = photon_pt[0] * math.sin(photon_phi[0])
    pz_0 = photon_pt[0] * math.sinh(photon_eta[0])
    px_1 = photon_pt[1] * math.cos(photon_phi[1])
    py_1 = photon_pt[1] * math.sin(photon_phi[1])
    pz_1 = photon_pt[1] * math.sinh(photon_eta[1])
    sumpx = px_0 + px_1
    sumpy = py_0 + py_1
    sumpz = pz_0 + pz_1
    sump = math.sqrt(sumpx**2 + sumpy**2 + sumpz**2)
    sumE = photon_E[0] + photon_E[1]
    return math.sqrt(sumE**2 - sump**2) / 1000  # Convert from MeV to GeV

def cut_photon_reconstruction(photon_isTightID):
    return photon_isTightID[0] == True and photon_isTightID[1] == True

def cut_photon_pt(photon_pt):
    return photon_pt[0] > 40000 and photon_pt[1] > 30000

def cut_isolation_et(photon_etcone20):
    return photon_etcone20[0] < 4000 and photon_etcone20[1] < 4000

def cut_photon_eta_transition(photon_eta):
    return (abs(photon_eta[0]) > 1.52 or abs(photon_eta[0]) < 1.37) and (abs(photon_eta[1]) > 1.52 or abs(photon_eta[1]) < 1.37)

# File reading and processing
def read_file(path, sample):
    logging.info(f"Accessing: {path}")
    try:
        tree = uproot.open(path + ":mini")
        logging.info(f"File opened successfully: {sample}")
    except Exception as e:
        logging.error(f"Error accessing file {path}: {e}")
        return pd.DataFrame()

    numevents = tree.num_entries
    logging.info(f"{sample}: Total events = {numevents}")

    data_all = pd.DataFrame()
    for data in tree.iterate(
        ["photon_pt", "photon_eta", "photon_phi", "photon_E", "photon_isTightID", "photon_etcone20"],
        library="pd",
        entry_stop=numevents * fraction,
    ):
        try:
            nIn = len(data)
            data = data[np.vectorize(cut_photon_reconstruction)(data.photon_isTightID)]
            data = data[np.vectorize(cut_photon_pt)(data.photon_pt)]
            data = data[np.vectorize(cut_isolation_et)(data.photon_etcone20)]
            data = data[np.vectorize(cut_photon_eta_transition)(data.photon_eta)]
            data['myy'] = np.vectorize(calc_myy)(
                data.photon_pt, data.photon_eta, data.photon_phi, data.photon_E
            )
            nOut = len(data)
            logging.info(f"{sample}: Batch processed, nIn={nIn}, nOut={nOut}")
            data_all = pd.concat([data_all, data], ignore_index=True)
        except Exception as e:
            logging.error(f"Error in batch processing for {sample}: {e}")
            continue

    logging.info(f"Finished processing {sample}. Total events: {len(data_all)}")
    return data_all

# Plotting
def plot_data(data):
    xmin = 100  # GeV
    xmax = 160  # GeV
    step_size = 3  # GeV

    bin_edges = np.arange(start=xmin, stop=xmax + step_size, step=step_size)
    bin_centres = bin_edges[:-1] + step_size / 2

    data_x, _ = np.histogram(data['myy'], bins=bin_edges)
    data_x_errors = np.sqrt(data_x)

    polynomial_mod = PolynomialModel(4)
    gaussian_mod = GaussianModel()

    pars = polynomial_mod.guess(data_x, x=bin_centres, c0=data_x.max())
    pars += gaussian_mod.guess(data_x, x=bin_centres, amplitude=100, center=125, sigma=2)
    model = polynomial_mod + gaussian_mod
    out = model.fit(data_x, pars, x=bin_centres, weights=1 / data_x_errors)

    params_dict = out.params.valuesdict()
    background = sum(
        params_dict[f'c{i}'] * bin_centres**i for i in range(5)
    )

    signal_x = data_x - background

    plt.axes([0.1,0.3,0.85,0.65]) # left, bottom, width, height 
    main_axes = plt.gca() # get current axes
    
    # plot the data points
    main_axes.errorbar(x=bin_centres, y=data_x, yerr=data_x_errors, 
                       fmt='ko', # 'k' means black and 'o' means circles
                       label='Data' ) 
    
    # plot the signal + background fit
    main_axes.plot(bin_centres, # x
                   out.best_fit, # y
                   '-r', # single red line
                   label='Sig+Bkg Fit ($m_H=125$ GeV)' )
    
    # plot the background only fit
    main_axes.plot(bin_centres, # x
                   background, # y
                   '--r', # dashed red line
                   label='Bkg (4th order polynomial)' )

    # set the x-limit of the main axes
    main_axes.set_xlim( left=xmin, right=xmax ) 
    
    # separation of x-axis minor ticks
    main_axes.xaxis.set_minor_locator( AutoMinorLocator() ) 
    
    # set the axis tick parameters for the main axes
    main_axes.tick_params(which='both', # ticks on both x and y axes
                          direction='in', # Put ticks inside and outside the axes
                          top=True, # draw ticks on the top axis
                          labelbottom=False, # don't draw tick labels on bottom axis
                          right=True ) # draw ticks on right axis
    
    # write y-axis label for main axes
    main_axes.set_ylabel('Events / '+str(step_size)+' GeV', 
                         horizontalalignment='right') 
    
    # set the y-axis limit for the main axes
    main_axes.set_ylim( bottom=0, top=np.amax(data_x)*1.1 ) 
    
    # set minor ticks on the y-axis of the main axes
    main_axes.yaxis.set_minor_locator( AutoMinorLocator() ) 
    
    # avoid displaying y=0 on the main axes
    main_axes.yaxis.get_major_ticks()[0].set_visible(False) 

    # Add text 'ATLAS Open Data' on plot
    plt.text(0.2, # x
             0.92, # y
             'ATLAS Open Data', # text
             transform=main_axes.transAxes, # coordinate system used is that of main_axes
             fontsize=13 ) 
    
    # Add text 'for education' on plot
    plt.text(0.2, # x
             0.86, # y
             'for education', # text
             transform=main_axes.transAxes, # coordinate system used is that of main_axes
             style='italic',
             fontsize=8 ) 
    
    # Add energy and luminosity
    lumi_used = str(lumi*fraction) # luminosity to write on the plot
    plt.text(0.2, # x
             0.8, # y
             '$\sqrt{s}$=13 TeV,$\int$L dt = '+lumi_used+' fb$^{-1}$', # text
             transform=main_axes.transAxes ) # coordinate system used is that of main_axes 
    
    # Add a label for the analysis carried out
    plt.text(0.2, # x
             0.74, # y
             r'$H \rightarrow \gamma\gamma$', # text 
             transform=main_axes.transAxes ) # coordinate system used is that of main_axes

    # draw the legend
    main_axes.legend(frameon=False, # no box around the legend
                     loc='lower left' ) # legend location 


    # *************
    # Data-Bkg plot 
    # *************
    plt.axes([0.1,0.1,0.85,0.2]) # left, bottom, width, height
    sub_axes = plt.gca() # get the current axes
    
    # set the y axis to be symmetric about Data-Background=0
    sub_axes.yaxis.set_major_locator( MaxNLocator(nbins='auto', 
                                                  symmetric=True) )
    
    # plot Data-Background
    sub_axes.errorbar(x=bin_centres, y=signal_x, yerr=data_x_errors,
                      fmt='ko' ) # 'k' means black and 'o' means circles
    
    # draw the fit to data
    sub_axes.plot(bin_centres, # x
                  out.best_fit-background, # y
                  '-r' ) # single red line
    
    # draw the background only fit
    sub_axes.plot(bin_centres, # x
                  background-background, # y
                  '--r' )  # dashed red line
    
    # set the x-axis limits on the sub axes
    sub_axes.set_xlim( left=xmin, right=xmax ) 
    
    # separation of x-axis minor ticks
    sub_axes.xaxis.set_minor_locator( AutoMinorLocator() ) 
    
    # x-axis label
    sub_axes.set_xlabel(r'di-photon invariant mass $\mathrm{m_{\gamma\gamma}}$ [GeV]',
                        x=1, horizontalalignment='right', 
                        fontsize=13 ) 
    
    # set the tick parameters for the sub axes
    sub_axes.tick_params(which='both', # ticks on both x and y axes
                         direction='in', # Put ticks inside and outside the axes
                         top=True, # draw ticks on the top axis
                         right=True ) # draw ticks on right axis 
    
    # separation of y-axis minor ticks
    sub_axes.yaxis.set_minor_locator( AutoMinorLocator() ) 
    
    # y-axis label on the sub axes
    sub_axes.set_ylabel( 'Events-Bkg' ) 


    # Generic features for both plots
    main_axes.yaxis.set_label_coords( -0.09, 1 ) # x,y coordinates of the y-axis label on the main axes
    sub_axes.yaxis.set_label_coords( -0.09, 0.5 ) # x,y coordinates of the y-axis label on the sub axes
    
    return
