use pyo3::prelude::*;

#[pyfunction]
fn compute_performance(buy_price: f64, current_price: f64, quantity: f64) -> PyResult<(f64,f64)>{
    let initial_value = buy_price * quantity;
    let current_value = current_price * quantity;

    let profit = current_value - initial_value;
    let roi = if initial_value != 0.0 {
        (profit / initial_value) * 100.0
    }
    else {
        0.0
    };

    Ok((roi,profit))
}

#[pymodule]
fn himid_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_performance,m)?)?;
    Ok(())
}