// globals
let mean = [];
let sigma = [];
let nominal = [];
let alpha = 0;
let alphaSigma = 0;
let validDimensions = false;
let validSkew = false;
let innerOuter = true;
let offNominal = false;

let expectedShrinkage = 0;

let xerror = 0;
let xsigma = 0;
let yerror = 0;
let ysigma = 0;

let possibleShrinkage = false;
let tooBig = false;
let dimsCalibrated = false;

function     hideMeasurementRows()
{

  let worksheet = document.getElementById('spreadsheet').jspreadsheet;

  let M = Number(document.getElementById('numMeasPts').value);


  for (let ii = 0; ii <= 27; ii++)
  {
    worksheet.showRow(ii);
  }

  if (M < 5)
  {
    worksheet.hideRow(4);
    worksheet.hideRow(9);
    worksheet.hideRow(14);
    worksheet.hideRow(19);
    worksheet.hideRow(23);
    worksheet.hideRow(27);
  }

  if (M < 4)
  {
    worksheet.hideRow(3);
    worksheet.hideRow(8);
    worksheet.hideRow(13);
    worksheet.hideRow(18);
    worksheet.hideRow(22);
    worksheet.hideRow(26);
  }

  if (M < 3)
  {
    worksheet.hideRow(2);
    worksheet.hideRow(7);
    worksheet.hideRow(12);
    worksheet.hideRow(17);
    worksheet.hideRow(21);
    worksheet.hideRow(25);
  }

  worksheet.removeMerge('A1');
  worksheet.removeMerge('A6');
  worksheet.removeMerge('A11');
  worksheet.removeMerge('A16');
  worksheet.removeMerge('A21');
  worksheet.removeMerge('A25');

  worksheet.removeMerge('B1');
  worksheet.removeMerge('B6');
  worksheet.removeMerge('B11');
  worksheet.removeMerge('B16');
  worksheet.removeMerge('B21');
  worksheet.removeMerge('B25');


  worksheet.setMerge('A1', 1, M);
  worksheet.setMerge('A6', 1, M);
  worksheet.setMerge('A11', 1, M);
  worksheet.setMerge('A16', 1, M);

  worksheet.setMerge('B1', 1, M);
  worksheet.setMerge('B6', 1, M);
  worksheet.setMerge('B11', 1, M);
  worksheet.setMerge('B16', 1, M);
  if (M > 2)
  {
    worksheet.setMerge('A21', 1, M-1);
    worksheet.setMerge('A25', 1, M-1);
    worksheet.setMerge('B21', 1, M-1);
    worksheet.setMerge('B25', 1, M-1);
  }


}

dot = (a, b) => a.map((x, i) => a[i] * b[i]).reduce((m, n) => m + n);

range = (a,b) => Array(b-a + 1).fill(a).map((x, y) => x + y);

const calculateSum = (arr) => {
    return arr.reduce((total, current) => {
        if (isNaN(current)){
          return total;
        }
        else{
          return total + current
        };
    }, 0);
}

// add and multiply two arrays component-wise
function add(a,b){
    return a.map((x,i) => x + b[i]);
}

function mult(a,b){
    return a.map((x,i) => x * b[i]);
}


/*
 * setNominals - Creates nominal values for each measurement points
 * Run whenever updating the number of measurement points, the size
 * of the print, or the scale
 */

function setNominals()
{

  let worksheet = document.getElementById('spreadsheet').jspreadsheet;

  let M = Number(document.getElementById('numMeasPts').value);
  let N = Number(document.getElementById('calistarSize').value);

  let printScale = Number(document.getElementById('printScale').value);
  // column that holds the nominal measurements
  let nomCol = 6;

  for (let ii = 0; ii < 5; ii++)
  {
    nominal[ii] = String( Math.max( (N - N*ii/M)*printScale,0) );
    if ( nominal[ii] == 0 )
    {
      nominal[ii] = NaN;
    }
    worksheet.setValueFromCoords(nomCol, ii, nominal[ii], true);
    worksheet.setValueFromCoords(nomCol, ii + 5, nominal[ii], true);
    worksheet.setValueFromCoords(nomCol, ii + 10, nominal[ii], true);
    worksheet.setValueFromCoords(nomCol, ii + 15, nominal[ii], true);
  }


  for (let ii = 0; ii < 4; ii++)
  {
    nominal[ii] = String( Math.max( (N - N*ii/M)*printScale,0) );
    if ( nominal[ii] == 0 )
    {
      nominal[ii] = NaN;
    }
    if (ii < M - 1 )

    {
      worksheet.setValueFromCoords(nomCol, ii + 20, nominal[ii], true);
      worksheet.setValueFromCoords(nomCol, ii + 24, nominal[ii], true);
    }
    else
    {
      worksheet.setValueFromCoords(nomCol, ii + 20, 0, true);
      worksheet.setValueFromCoords(nomCol, ii + 24, 0, true);
    }
  }


  nominal = extractColumnVector(range(0,28), nomCol);

}


/*
 * changeNumMeasPts - Run whenever the number of measurement points is changed
 */
function changeNumMeasPts()
{
  hideMeasurementRows();
  setNominals();
  let N = String(document.getElementById('numMeasPts').value);
  document.getElementById('calistar_MxN').src = 'img/meas_pts_' + N + '.svg';
  // TODO: need a more robust way to do this
  document.getElementsByClassName('glightbox')[0].href = 'img/meas_pts_' + N + '.svg';
  if (typeof(lightbox) != 'undefined')
  {
    lightbox.reload();
  } 
}

function updateDimensionality()
{

  // x dimensions are rows 0 - 9
  let results = calculateDimensionality(range(0,9));

  dom = document.getElementById('xerror');
  xerror = results[0];
  dom.innerHTML = String((xerror*100).toPrecision(3)) + '%';

  dom = document.getElementById('xsigma');
  xsigma = results[1];
  dom.innerHTML = String((xsigma*100).toPrecision(3)) + '%';

  dom = document.getElementById('xcorrection');
  dom.innerHTML = String((-results[0]*100).toPrecision(3)) + '%';

  document.getElementById('xNumSigma').innerHTML = String( (xerror/xsigma).toFixed(1) );

  // y dimensions are rows 10 - 19
  results = calculateDimensionality(range(10,19));

  dom = document.getElementById('yerror');

  yerror = results[0];
  dom.innerHTML = String((100*yerror).toPrecision(3)) + '%';

  dom = document.getElementById('ysigma');
  ysigma = results[1];
  dom.innerHTML = String((100*ysigma).toPrecision(3)) + '%';
  let ycorrection = document.getElementById('ycorrection');
  ycorrection.innerHTML = String((-results[0]*100).toPrecision(3)) + '%';

  document.getElementById('yNumSigma').innerHTML = String( (yerror/ysigma).toFixed(1) );

  dom = document.getElementById('yourCorrection');
  dom.innerHTML = '(' + String((xerror*100).toFixed(2)) + '%, ' + String((yerror*100).toFixed(2)) + '%)'

  data = document.getElementById('dimGraph').data;
  data[0]['x'] = [yerror*100,xerror*100];
  data[0]['error_x']['array'] = [2*ysigma*100,2*xsigma*100];

  data[1]['x'] = [yerror*100,xerror*100];
  data[1]['error_x']['array'] = [ysigma*100,xsigma*100];
  
  Plotly.redraw('dimGraph');

}

function updateShrinkageFeedback()
{


  dimsCalibrated = ( Math.abs(xerror) < 2*xsigma ) & ( Math.abs(yerror) < 2*ysigma );
  tooBig = ( xerror > 2*xsigma) || ( yerror > 2 * ysigma );
  

  let xysame = ( Math.abs(xerror - yerror) < 2*Math.sqrt(xsigma*xsigma + ysigma*ysigma) );
  let inbounds = (xerror < 3*xsigma) & (yerror < 3*ysigma) &
                 ( (xerror - 2*xsigma) > -0.016)  &
                 ( (yerror - 2*ysigma) > -0.016);

  let inboundsMat = (xerror < 3*xsigma) & (yerror < 3*ysigma) &
                      ( (xerror - 2*xsigma) > -expectedShrinkage)  &
                      ( (yerror - 2*ysigma) > -expectedShrinkage);

  probableShrinkage = xysame & inbounds;

  document.getElementById('possibleShrinkage').style.display = "none";
  document.getElementById('printTooBig').style.display = "none";
  document.getElementById('probableShrinkage').style.display = "none";
  document.getElementById('probablyNotShrinkage').style.display = "none";
  if ( dimsCalibrated )
  {
    // dimensions look good, suggest doing nothing
  }
  else if (xysame & !tooBig & inbounds)
  {
    // possibly shrinkage, request info on material
    document.getElementById('possibleShrinkage').style.display = "";

    if ( inboundsMat )
    {
      document.getElementById('probableShrinkage').style.display = "";
    }
    else
    {
      document.getElementById('probablyNotShrinkage').style.display = "";
    }
  }
  else if ( tooBig )
  {
    document.getElementById('printTooBig').style.display = "";
  }
  else
  {
    // not shrinkage
    document.getElementById('probablyNotShrinkage').style.display = "";
  }

/*
  if ( tooBig )
  {
    document.getElementById('printTooBig').style.display = "";
  }
  else if (!isNaN(xerror) & !isNaN(yerror) )
  {
    document.getElementById('possibleShrinkage').style.display = "";
    if ( probableShrinkage)
    {
      document.getElementById('probableShrinkage').style.display = "";
    }
    else
    {
      document.getElementById('probablyNotShrinkage').style.display = "";
    }
  }*/

}

// calculate the dimensionality of an axis whose data is held in rows
function calculateDimensionality(rows)
{
  let numValid = 0;
  let sum      = 0;
  let sumsq    = 0;
  let sigma0   = 0;
  if ( document.getElementById('sample_error').checked)
  {
      sigma0 = Number(document.getElementById('caliper_error').value)   ;
  }

  for (const row of rows)
  {
    let results = [mean[row], sigma[row], numValidMeasurements[row]];//meanAndStd(row, [3,4,5]);
    let nom = nominal[row];//Number(worksheet.getValueFromCoords(6,row));

    if ( !isNaN(results[0]) & !isNaN(nom) ) // valid entry
    {
      let del = (mean[row] - nom)/nom;
      sum += del;
      // gradient term
      let sigma2 = sigma[row]*sigma[row] + sigma0*sigma0;
      numValid++;
      sumsq += sigma2/(nom*nom);
    }
  }
  return([sum/numValid, Math.sqrt(sumsq/(numValid*numValid)), numValid]);

}

// calculate the mean and standard dev of data in specified row and columns
// Uses 1/(N-1) for standard deviation, but uses convention that only one pt has a std = 0
/*
function meanAndStd(row, cols)
{
  let sum = 0;
  let v = 0;
  let numValid = 0;

  w = extractRowVector(row, cols);
  sum = calculateSum(w);
  numValid = calculateSum( w.map((x) => x > 0) );

  let mean = sum/numValid;

  wMinusMean = w.map( (x) => (x - mean)*(x > 0) );
  let sumsq  = dot(wMinusMean, wMinusMean);

  let sigma = 0;
  if (numValid > 0)
  {
    sigma = Math.sqrt(sumsq/(numValid-1));
  }

  console.log([mean, sigma, numValid]);
  return [mean, sigma, numValid];


}*/

function sumColumn(rows, col)
{
  let sum = 0;
  for (const row of rows)
  {
    v = Number(worksheet.getValueFromCoords(col,row));
    if (v > 0)
    {
      sum += v;
    }

  }
  return sum;
}


function computeTotalLength(rows)
{
  let sum = 0;
  for (const row of rows)
  {
    /*let rowMean = meanAndStd(row, [3,4,5]);
    if (rowMean[2] > 0)
    {
      sum += rowMean[0];
    }*/
    if ( numValidMeasurements[row] > 0 )
    {
      sum += mean[row];
    }

  }
  let nominalSum = sumColumn(rows, 6);

  return sum/nominalSum;
}

function calculateSkew()
{

  function sig2(start,end){
    let s = sigma.slice(start,end);
    let n = nominal.slice(start,end);
    let sigma0 = 0;
    s = mult(s,n.map((x) => x>0));
    if ( document.getElementById('sample_error').checked)
    {
        sigma0 = Number(document.getElementById('caliper_error').value);
    }
    return (dot(s,s) + sigma0*sigma0)/(calculateSum(n)*calculateSum(n));

  }

  let p = computeTotalLength([20,21,22,23]);
  let sig2p =  sig2(20,24);
  

  let q = computeTotalLength([24,25,26,27]);
  let sig2q = sig2(24,28);


  let a = computeTotalLength([0,1,2,3,4])*Math.sqrt(2)/2;
  let sig2a = sig2(0,5)*1/2;;


  let b = computeTotalLength([10,11,12,13,14])*Math.sqrt(2)/2;
  let sig2b = sig2(10,15)*1/2;


  let cosAlpha = (p*p - q*q)/(4*a*b);
  let alphaRad = Math.acos(cosAlpha);
  alpha    = alphaRad*180/Math.PI;
  let sinAlpha = Math.sin(alphaRad);
  // gradient calculation
  let gradp = Math.abs(p/(2*a*b*sinAlpha));
  let gradq = Math.abs(q/(2*a*b*sinAlpha));
  let grada = Math.abs((p*p-q*q)/(4*a*a*b*sinAlpha));
  let gradb = Math.abs((p*p-q*q)/(4*a*b*b*sinAlpha));


  alphaSigma = Math.sqrt(dot([gradp*gradp,gradq*gradq,grada*grada,gradb*gradb], [sig2p,sig2q,sig2a,sig2b]))*180/Math.PI;


  return [alpha,alphaSigma];

}

function updateSkew()
{
  let v = calculateSkew();
  alpha = v[0];
  alphaSigma = v[1];

  let dom = document.getElementById('parAngle');
  dom.innerHTML = String((alpha).toFixed(5));

  //dom = document.getElementById('parSigma');
  //dom.innerHTML = String((alphaSigma).toFixed(5));

  //dom = document.getElementById('parCorrection');
  //dom.innerHTML = String((90-alpha).toFixed(5));


  //document.getElementById('parNumSigmas').innerHTML = String( ((90 - alpha)/alphaSigma).toFixed(1) );



  dom = document.getElementById('skewAngle');
  dom.innerHTML = String((alpha - 90).toPrecision(3));

  dom = document.getElementById('skewSigma');
  dom.innerHTML = String((alphaSigma).toPrecision(3));

  dom = document.getElementById('skewCorrection');
  dom.innerHTML = String((90-alpha).toPrecision(3));

  document.getElementById('skewNumSigmas').innerHTML = String( ((90 - alpha)/alphaSigma).toPrecision(2  ) );

  document.getElementById('skew-1sigma').style.display = "none";
  document.getElementById('skew-2sigma').style.display = "none";
  document.getElementById('skew-3sigma').style.display = "none";
  document.getElementById('skewFailure').style.display = "none";

  let str = '';
  if ( (Math.abs(alpha - 90) / alphaSigma) < 1)
  {
    document.getElementById('skew-1sigma').style.display = "";
  }
  else if ( (Math.abs(alpha - 90) / alphaSigma) < 2)
  {
    document.getElementById('skew-2sigma').style.display = "";
  }
  else if ( (Math.abs(alpha - 90) / alphaSigma) < 3)
  {
    document.getElementById('skew-3sigma').style.display = "";
  }
  else if (!isNaN(alpha))
  {
    document.getElementById('skewFailure').style.display = "";
  }

  data = document.getElementById('skewGraph').data;
  data[0]['x'] = [alpha - 90];
  data[0]['error_x']['array'] = [2*alphaSigma];

  data[1]['x'] = [alpha - 90];
  data[1]['error_x']['array'] = [alphaSigma];
  
  Plotly.redraw('skewGraph');
  //document.getElementById('skewFeedback').innerHTML = str;

}


function extractColumnVector(rows, col)
{
  let v = [];
  for (let ii = 0; ii < rows.length; ii++)
  {
    v[ii] = Number(worksheet.getValueFromCoords(col,rows[ii]));
  }
  return v;
}



function extractRowVector(row, cols)
{
  let v = [];
  for (let ii = 0; ii < cols.length; ii++)
  {
    v[ii] = Number(worksheet.getValueFromCoords(cols[ii],row));
  }
  return v;
}

// returns a vector that is true if an input is expected
// by checking if the nominal value is > 0
function inputExpected()
{
  let w = extractColumnVector(range(0,27),6);
  w = w.map( (x) => x > 0);
  return w;
}

let numValidMeasurements = [];

function updateNumValidMeasurements()
{
  for (let ii = 0; ii < 28; ii++)
  {
    let w = extractRowVector(ii,[3,4,5]);
    numValidMeasurements[ii] = calculateSum( w.map( (x) => x > 0 ) );
  }
}


function updateMean()
{
  updateNumValidMeasurements();
  for (let ii = 0; ii < 28; ii++)
  {
    let w = extractRowVector(ii,[3,4,5]);
    let s = calculateSum( mult(w, w.map( (x) => x > 0) ) );
    mean[ii] = s/numValidMeasurements[ii];
  }
}

function updateSigma()
{
  updateMean();
  
  for (let ii = 0; ii < 28; ii++)
  {
    let w = extractRowVector(ii,[3,4,5]);
    w = w.map( (x) => (x - mean[ii]) * (x > 0) );
    let s2 = dot(w, w);
    if (numValidMeasurements[ii] > 1)
    {
      sigma[ii] = Math.sqrt(s2/(numValidMeasurements[ii] - 1));
    }
    else
    {
      sigma[ii] = 0 ;
    }
  }
}

function updateXYSteps()
{

  let marlincorexy = document.getElementById('marlincorexy').checked;
  let xstep = Number(document.getElementById('xstep').value);
  if ( xstep == 0 ){ xstep = 80.000 }; //use placeholder

  let ystep = Number(document.getElementById('ystep').value);
  if ( ystep == 0 ){ ystep = 80.000 }; //use placeholder

  let resultsx = 0;
  let resultsy = 0;
  if (marlincorexy)
  {
    resultsx = calculateSum(mult(nominal.slice(0,20), mean.map( (x) => !isNaN(x))))/calculateSum(mean.slice(0,20));
    //let xsteps  =
    resultsy = resultsx;
  }
  else
  {
    resultsx = calculateSum(mult(nominal.slice(0,10), mean.map( (x) => !isNaN(x))))/calculateSum(mean.slice(0,10));
    //let xsteps  =
    resultsy = calculateSum(mult(nominal.slice(10,20), mean.map( (x) => !isNaN(x))))/calculateSum(mean.slice(10,20));
  }
  xstep = (xstep*resultsx).toFixed(3);
  ystep = (ystep*resultsy).toFixed(3);

  let str = "M92 X" + String(xstep) + " Y" + ystep + "; updates x- and y-steps with your values"

  let dom = document.getElementById('__span-marlindimensions-1');
  dom.innerHTML = str;

}


function updateXYRotation()
{

  let klippercorexy = document.getElementById('klippercorexy').checked;
  let xstep = Number(document.getElementById('oldStepperX').value);
  if ( xstep == 0 ){ xstep = 40.000 }; //use placeholder

  let ystep = Number(document.getElementById('oldStepperY').value);
  if ( ystep == 0 ){ ystep = 40.000 }; //use placeholder

  let resultsx = 0;
  let resultsy = 0;
  if (klippercorexy)
  {
    resultsx = calculateSum(mult(nominal.slice(0,20), mean.map( (x) => !isNaN(x))))/calculateSum(mean.slice(0,20));
    //let xsteps  =
    resultsy = resultsx;
  }
  else
  {
    resultsx = calculateSum(mult(nominal.slice(0,10), mean.map( (x) => !isNaN(x))))/calculateSum(mean.slice(0,10));
    //let xsteps  =
    resultsy = calculateSum(mult(nominal.slice(10,20), mean.map( (x) => !isNaN(x))))/calculateSum(mean.slice(10,20));
  }
  xstep = (xstep/resultsx).toFixed(3);
  ystep = (ystep/resultsy).toFixed(3);

  let strx = "rotation_distance: " + String(xstep);
  let stry = "rotation_distance: " + String(ystep);

  let dom = document.getElementById('__span-klipper_stepper_x-1');
  dom.innerHTML = strx;

  dom = document.getElementById('__span-klipper_stepper_y-1');
  dom.innerHTML = stry;

}

/*
 * Update shrinkage settings in slicer
 */
function updateShrinkage()
{

  results = calculateSum(mult(nominal.slice(0,20), mean.map( (x) => !isNaN(x))))/calculateSum(mean.slice(0,20));

  let shrinkage = Number(document.getElementById('oldShrinkage').value);
  if ( shrinkage == 0 ){ shrinkage = 100 }; //use placeholder

  // Shrinkage in Superslicer refers to how large the print actually comes out divided by nominal size
  let dom = document.getElementById('shrinkage');
  dom.innerHTML = String((shrinkage/results).toFixed(3)) + "%";

  document.getElementById('slicerscaling').innerHTML = String((results/shrinkage*10000).toFixed(3)); 
}


function updateSkewKlipper()
{
  let oldP = Number(document.getElementById('oldAC').value); //
  if (oldP == 0){ oldP = 100; }

  let oldQ = Number(document.getElementById('oldBD').value); // BD
  if (oldQ == 0){ oldQ = 100; }

  let oldB = Number(document.getElementById('oldAD').value); // AD
  if (oldB == 0){ oldB = 100*Math.sqrt(2)/2; }
  let oldA = Math.sqrt(1/2*(oldP*oldP + oldQ*oldQ - 2 * oldB*oldB)); // sqrt(1/2*(p^2+q^2 - 2 b^2))
  let oldAlpha = Math.acos(( oldP*oldP - oldQ*oldQ )/(4*oldA*oldB)); // acos( (p^2 - q^2)/(4*a*b) )
  let oldCorrection = Math.PI/2 - oldAlpha;
  let totalCorrection = oldCorrection - (alpha*Math.PI/180 - Math.PI/2)

  let newP = Math.sqrt(100*100 - 100*100*Math.cos(totalCorrection + Math.PI/2));
  let newQ = Math.sqrt(100*100 + 100*100*Math.cos(totalCorrection + Math.PI/2));
  let newB = Math.sqrt(2)/2*100;

  document.getElementById('newAC').innerHTML = newP.toFixed(5);
  document.getElementById('newBD').innerHTML = newQ.toFixed(5);
  document.getElementById('newAD').innerHTML = newB.toFixed(5);

  document.getElementById('oldCorrection').innerHTML = (oldCorrection*180/Math.PI).toFixed(5);
  document.getElementById('totalCorrection').innerHTML = (totalCorrection*180/Math.PI).toFixed(5);

  let str = "SET_SKEW XY=" + String(newP.toFixed(5)) + "," + String(newQ.toFixed(5)) + "," + String(newB.toFixed(5));
  document.getElementById('__span-klipperskew-1').innerHTML = str;

  str = "CALC_MEASURED_SKEW AC=" + String(newP.toFixed(5)) + " BD=" + String(newQ.toFixed(5)) + " AD=" + String(newB.toFixed(5));
  document.getElementById('__span-klippercalcskew-1').innerHTML = str;


}




function updateSkewMarlin()
{
  let skewFactor = Math.tan( (90 - alpha)*Math.PI/180 );

  let str = "M582 I" + String(skewFactor.toFixed(5)) + "; sets the skew factor";

  document.getElementById('__span-marlinskew-1').innerHTML = str;



}

function update()
{
  updateMaterial();
  updateSigma(); // triggers mean update and numValidMeasurements update
  validateMeasurements();
  updateDimensionality();
  updateShrinkage();
  updateShrinkageFeedback();
  updateSkew();
  updateXYSteps();
  updateXYRotation();
  updateSkewKlipper();
  updateSkewMarlin();

}


function validateMeasurements()
{
  // validate that at least one x, one y, one D, and one d measurement are valid
  let validx = calculateSum(mean.slice(0,10) ) > 0;
  let validy = calculateSum(mean.slice(10,20)) > 0;
  let validD = calculateSum(mean.slice(20,24)) > 0;
  let validd = calculateSum(mean.slice(24,28)) > 0;

  validDimensions = validx & validy;
  validSkew       = validx & validy & validD & validd;

  // determine if any measurements are off nominal
  let cols = ['D', 'E', 'F']
  offNominal = false;
  for (let ii = 0; ii < 28; ii++)
  {
    if ( nominal[ii] > 0 )
    {
      let v = extractRowVector(ii,[3,4,5]);
      for (let jj = 0; jj < 3; jj++)
      {
        if ( Math.abs(nominal[ii] - v[jj]) > 0.5 && v[jj] > 0)
        {
          offNominal = true;
          break;
        }
      }
    }
  }

  innerOuter = true;
  // x inner outer
  for (let ii = 0; ii < 5; ii++)
  {
    if ( nominal[ii] > 0 )
    {
      let v = extractRowVector(ii    ,[3,4,5]);
      let w = extractRowVector(ii + 5,[3,4,5]);
      for (let jj = 0; jj < 3; jj++)
      {

        if ( (v[jj] > 0) != (w[jj] > 0)  )
        {
          innerOuter = false;
          worksheet.setStyle(cols[jj] + String(ii+1), 'background-color', 'yellow');
          //console.log(cols[jj] + String(ii+1), 'background-color', 'yellow');
        }
        else
        {
          //console.log('reset ' + cols[jj] + String(ii + 6));
          worksheet.resetStyle(cols[jj] + String(ii+6));
        }
      }
    }
  }


  // y inner outer
  for (let ii = 10; ii < 15; ii++)
  {
    if ( nominal[ii] > 0 )
    {
      let v = extractRowVector(ii    ,[3,4,5]);
      let w = extractRowVector(ii + 5,[3,4,5]);
      for (let jj = 0; jj < 3; jj++)
      {

        if ( (v[jj] > 0) != (w[jj] > 0)  )
        {
          innerOuter = false;
          break;
        }
      }
    }
  }

  showMeasurementWarnings();

}


function showMeasurementWarnings()
{
  // 'none' hides, '' shows it
  if (offNominal)
  {
    document.getElementById('outoffamily').style.display = "";
  }
  else
  {
    document.getElementById('outoffamily').style.display = "none";
  }

  if (!validDimensions)
  {
    document.getElementById('validDimensions').style.display = "";
    document.getElementById('dimensionFeedback').style.display = "";

    document.getElementById('dimension-1sigma').style.display = "none";
    document.getElementById('dimension-2sigma').style.display = "none";
    document.getElementById('dimension-3sigma').style.display = "none";
    document.getElementById('dimensionFailure').style.display = "none";
  }
  else
  {
    document.getElementById('validDimensions').style.display = "none";
    document.getElementById('dimensionFeedback').style.display = "none";
    document.getElementById('dimensionsLookGood').style.display = "none";
    document.getElementById('dimensionNeedAdjusted').style.display = "none";



    // check how many stds we're calibrated to within
    let howManySigs = Math.max(Math.abs(xerror/xsigma),Math.abs(yerror/ysigma));
    document.getElementById('dimension-1sigma').style.display = "none";
    document.getElementById('dimension-2sigma').style.display = "none";
    document.getElementById('dimension-3sigma').style.display = "none";
    document.getElementById('dimensionFailure').style.display = "none";
    if (howManySigs < 1)
    {
      document.getElementById('dimension-1sigma').style.display = "";
      document.getElementById('dimensionsLookGood').style.display = "";
    }
    else if (howManySigs < 2)
    {
      document.getElementById('dimension-2sigma').style.display = "";
      document.getElementById('dimensionsLookGood').style.display = "";
    }
    else if (howManySigs < 3)
    {
      document.getElementById('dimension-3sigma').style.display = "";
      document.getElementById('dimensionNeedAdjusted').style.display = "";
    }
    else
    {
      document.getElementById('dimensionFailure').style.display = "";
      document.getElementById('dimensionNeedAdjusted').style.display = "";
    }


  }

  if (!innerOuter)
  {
    document.getElementById('validInnerOuter').style.display = "";
  }
  else
  {
    document.getElementById('validInnerOuter').style.display = "none";
  }

  if (!validSkew)
  {
    document.getElementById('validSkew').style.display = "";
    document.getElementById('skewFeedback').style.display = "";
  }
  else
  {
    document.getElementById('validSkew').style.display = "none";
    document.getElementById('skewFeedback').style.display = "none";
  }

  if ( !offNominal & validDimensions & validSkew & innerOuter )
  {
    document.getElementById('measurementWarnings').style.display = "none";
    document.getElementById('valideverything').style.display = "";

  }
  else
  {
    document.getElementById('measurementWarnings').style.display = "";
    document.getElementById('valideverything').style.display = "none";
  }

}

function updateMaterial()
{
  let material = document.getElementById('materials').value;
  switch (material)
  {
    case 'PLA':
      expectedShrinkage = 0.003;
      break;
    case 'PETG':
      expectedShrinkage = 0.008;
      break;
    case 'ABS':
      expectedShrinkage = 0.016;
      break;
    default:
      expectedShrinkage = 1;
  }
  document.getElementById('expectedShrinkage').innerHTML = String(-expectedShrinkage*100) + '%';

  updateShrinkageFeedback();

}

window.onload = changeNumMeasPts();
