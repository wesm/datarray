''' Tests for DataArray and friends '''

import numpy as np

from datarray.datarray import Axis, DataArray, NamedAxisError, \
    _pull_axis, _reordered_axes

import nose.tools as nt
import numpy.testing as npt

def test_axis_equal():
    ax1 = Axis('aname', 0, None)
    ax2 = Axis('aname', 0, None)
    yield nt.assert_equal, ax1, ax2
    # The array to which the axis points does not matter in comparison
    ax3 = Axis('aname', 0, np.arange(10))
    yield nt.assert_equal, ax1, ax3
    # but the index does
    ax4 = Axis('aname', 1, None)
    yield nt.assert_not_equal, ax1, ax4
    # so does the name
    ax5 = Axis('anothername', 0, None)
    yield nt.assert_not_equal, ax1, ax5
    # and obviously both
    yield nt.assert_not_equal, ax4, ax5

def test_bad_ticks1():
    d = np.zeros(5)
    # bad ticks length
    nt.assert_raises(ValueError, DataArray, d, labels=[('a', 'uvw')])

def test_bad_ticks2():
    d = np.zeros(5)
    # uniqueness error
    nt.assert_raises(ValueError, DataArray, d, labels=[('a', ['u']*5)])

def test_bad_ticks3():
    d = np.zeros(5)
    # type error
    nt.assert_raises(ValueError, DataArray, d, labels=[('a', [1, 1, 1, 1, 1])])
    
def test_basic():
    adata = [2,3]
    a = DataArray(adata, 'x', float)
    yield nt.assert_equal, a.labels, ('x',)
    yield nt.assert_equal, a.dtype, np.dtype(float)
    b = DataArray([[1,2],[3,4],[5,6]], 'xy')
    yield nt.assert_equal, b.labels, ('x','y')
    # integer slicing
    b0 = b.axis.x[0]
    yield npt.assert_equal, b0, [1,2]
    # slice slicing
    b1 = b.axis.x[1:]
    yield npt.assert_equal, b1, [[3,4], [5,6]]


def test_combination():
    narr = DataArray(np.zeros((1,2,3)), labels=('a','b','c'))
    n3 = DataArray(np.ones((1,2,3)), labels=('x','b','c'))
    yield nt.assert_raises, NamedAxisError, np.add, narr, n3
    # addition of scalar
    res = narr + 2
    yield nt.assert_true, isinstance(res, DataArray)
    yield nt.assert_equal, res.axes, narr.axes
    # addition of matching size array, with matching names
    res = narr + narr
    yield nt.assert_equal, res.axes, narr.axes


def test_1d():
    adata = [2,3]
    a = DataArray(adata, 'x', int)
    # Verify scalar extraction
    yield (nt.assert_true,isinstance(a.axis.x[0],int))
    # Verify indexing of axis
    yield (nt.assert_equals, a.axis.x.index, 0)
    # Iteration checks
    for i,val in enumerate(a.axis.x):
        yield (nt.assert_equals,val,adata[i])
        yield (nt.assert_true,isinstance(val,int))


def test_2d():
    b = DataArray([[1,2],[3,4],[5,6]], 'xy')
    yield (nt.assert_equals, b.labels, ('x','y'))
    # Check row named slicing
    rs = b.axis.x[0]
    yield (npt.assert_equal, rs, [1,2])
    yield nt.assert_equal, rs.labels, ('y',)
    yield nt.assert_equal, rs.axes, (Axis('y', 0, rs),)
    # Now, check that when slicing a row, we get the right names in the output
    yield (nt.assert_equal, b.axis.x[1:].labels, ('x','y'))
    # Check column named slicing
    cs = b.axis.y[1]
    yield (npt.assert_equal, cs, [2,4,6])
    yield nt.assert_equal, cs.labels, ('x',)
    yield nt.assert_equal, cs.axes, (Axis('x', 0, cs),)
    # What happens if we do normal slicing?
    rs = b[0]
    yield (npt.assert_equal, rs, [1,2])
    yield nt.assert_equal, rs.labels, ('y',)
    yield nt.assert_equal, rs.axes, (Axis('y', 0, rs),)
    

def test__pull_axis():
    a = Axis('x', 0, None)
    b = Axis('y', 1, None)
    c = Axis('z', 2, None)
    t_pos = Axis('y', 1, None)
    t_neg = Axis('x', 5, None)
    axes = [a, b, c]
    yield nt.assert_true, t_pos in axes
    yield nt.assert_false, t_neg in axes
    yield nt.assert_equal, axes, _pull_axis(axes, t_neg)
    yield nt.assert_equal, axes[:-1], _pull_axis(axes, c)
    new_axes = [a, Axis('z', 1, None)]
    yield nt.assert_equal, new_axes, _pull_axis(axes, t_pos)
    

def test__reordered_axes():
    a = Axis('x', 0, None)
    b = Axis('y', 1, None)
    c = Axis('z', 2, None)
    res = _reordered_axes([a,b,c], (1,2,0))
    names_inds = [(ax.label, ax.index) for ax in res]
    yield nt.assert_equal, set(names_inds), set([('y',0),('z',1),('x',2)])

def test_axis_make_slice():
    p_arr = np.random.randn(2,4,5)
    ax_spec = 'capitals', ['washington', 'london', 'berlin', 'paris', 'moscow']
    d_arr = DataArray(p_arr, [None, None, ax_spec])
    a = d_arr.axis.capitals
    sl = a.make_slice( slice('london', 'moscow')  )
    should_be = ( slice(None), slice(None), slice(1,4) )
    yield nt.assert_equal, should_be, sl, 'slicing tuple from ticks not correct'
    sl = a.make_slice( slice(1,4) )
    yield nt.assert_equal, should_be, sl, 'slicing tuple from idx not correct'

# also test with the slicing syntax
def test_ticks_slicing():
    p_arr = np.random.randn(2,4,5)
    ax_spec = 'capitals', ['washington', 'london', 'berlin', 'paris', 'moscow']
    d_arr = DataArray(p_arr, [None, None, ax_spec])
    a = d_arr.axis.capitals
    sub_arr = d_arr.axis.capitals['washington'::2]
    yield (nt.assert_equal,
           sub_arr.axis.capitals.ticks,
           a.ticks[0::2])
    yield nt.assert_true, (sub_arr == d_arr[:,:,0::2]).all()

# -- Tests for redefined methods ---------------------------------------------
    
def test_transpose():
    b = DataArray([[1,2],[3,4],[5,6]], 'xy')
    bt = b.T
    c = DataArray([ [1,3,5], [2,4,6] ], 'yx')
    yield nt.assert_true, bt.axis.x.index == 1 and bt.axis.y.index == 0
    yield nt.assert_true, bt.shape == (2,3)
    yield nt.assert_true, (bt==c).all()

def test_swapaxes():
    n_arr = np.random.randn(2,4,3)
    a = DataArray(n_arr, 'xyz')
    b = a.swapaxes('x', 'z')
    c = DataArray(n_arr.transpose(2,1,0), 'zyx')
    yield nt.assert_true, (c==b).all(), 'data not equal in swapaxes test'
    for ax1, ax2 in zip(b.axes, c.axes):
        yield nt.assert_true, ax1==ax2, 'axes not equal in swapaxes test'

# -- Tests for wrapped ndarray methods ---------------------------------------

_failing_methods = ['ptp']
_other_wraps = ['argmax', 'argmin', 'argsort']
_methods = ['mean', 'var', 'std', 'min', 'max', 'sum', 'prod'] + _other_wraps
def assert_data_correct(d_arr, op, axis):
    from datarray.datarray import _names_to_numbers 
    super_opr = getattr(np.ndarray, op)
    axis_idx = _names_to_numbers(d_arr.axes, [axis])[0]
    d1 = np.asarray(super_opr(d_arr, axis=axis_idx))
    opr = getattr(d_arr, op)
    d2 = np.asarray(opr(axis=axis))
    assert (d1==d2).all(), 'data computed incorrectly on operation %s'%op

def assert_axes_correct(d_arr, op, axis):
    from datarray.datarray import _names_to_numbers, _pull_axis
    opr = getattr(d_arr, op)
    d = opr(axis=axis)
    axis_idx = _names_to_numbers(d_arr.axes, [axis])[0]
    axes = _pull_axis(d_arr.axes, d_arr.axes[axis_idx])
    assert all( [ax1==ax2 for ax1, ax2 in zip(d.axes, axes)] ), \
           'mislabeled axes from operation %s'%op

def test_wrapped_ops_data():
    a = DataArray(np.random.randn(4,2,6), 'xyz')
    for m in _methods:
        yield assert_data_correct, a, m, 'x'
    for m in _methods:
        yield assert_data_correct, a, m, 'y'
    for m in _methods:
        yield assert_data_correct, a, m, 'z'

def test_wrapped_ops_axes():
    a = DataArray(np.random.randn(4,2,6), 'xyz')
    for m in _methods:
        yield assert_axes_correct, a, m, 'x'
    for m in _methods:
        yield assert_axes_correct, a, m, 'y'
    for m in _methods:
        yield assert_axes_correct, a, m, 'z'
    
# -- Tests for slicing with "newaxis" ----------------------------------------
def test_newaxis_slicing():
    b = DataArray([[1,2],[3,4],[5,6]], 'xy')
    b2 = b[np.newaxis]
    yield nt.assert_true, b2.shape == (1,) + b.shape
    yield nt.assert_true, b2.axes[0].label == None

    b2 = b[:,np.newaxis]
    yield nt.assert_true, b2.shape == (3,1,2)
    yield nt.assert_true, (b2[:,0,:]==b).all()

# -- Testing broadcasting features -------------------------------------------
def test_broadcast():
    b = DataArray([[1,2],[3,4],[5,6]], 'xy')
    a = DataArray([1,0], 'y')
    # both of these should work
    c = b + a
    yield nt.assert_true, c.labels == ('x', 'y'), 'simple broadcast failed'
    c = a + b
    yield nt.assert_true, c.labels == ('x', 'y'), \
          'backwards simple broadcast failed'
    
    a = DataArray([1, 1, 1], 'x')
    # this should work too
    c = a[:,np.newaxis] + b
    yield nt.assert_true, c.labels == ('x', 'y'), 'forward broadcast1 failed'
    c = b + a[:,np.newaxis] 
    yield nt.assert_true, c.labels == ('x', 'y'), 'forward broadcast2 failed'

    b = DataArray(np.random.randn(3,2,4), ['x', None, 'y'])
    a = DataArray(np.random.randn(2,4), [None, 'y'])
    # this should work
    c = b + a
    yield nt.assert_true, c.labels == ('x', None, 'y'), \
          'broadcast with unlabeled dimensions failed'
    # and this
    a = DataArray(np.random.randn(2,1), [None, 'y'])
    c = b + a
    yield nt.assert_true, c.labels == ('x', None, 'y'), \
          'broadcast with matched label, but singleton dimension failed'

# -- Testing slicing failures ------------------------------------------------
@nt.raises(NamedAxisError)
def test_broadcast_fails1():
    a = DataArray( np.random.randn(2,5,6), 'xyz' )
    b = DataArray( np.random.randn(5,6), 'xz' )
    c = a + b

@nt.raises(ValueError)
def test_broadcast_fails2():
    a = DataArray( np.random.randn(2,5,6), 'xy' ) # last axis is unlabeled
    b = DataArray( np.random.randn(2,6,6), 'xy' )
    # this should fail simply because the dimensions are not matched
    c = a + b

@nt.raises(IndexError)
def test_indexing_fails():
    a = DataArray( np.random.randn(2,5,6), 'xy' )
    a[:2,:1,:2,:5]

@nt.raises(IndexError)
def test_ambiguous_ellipsis_fails():
    a = DataArray( np.random.randn(2,5,6), 'xy' )
    a[...,0,...]

def test_ellipsis_slicing():
    a = DataArray( np.random.randn(2,5,6), 'xy' )
    yield nt.assert_true, (a[...,0] == a[:,:,0]).all(), \
          'slicing with ellipsis failed'
    yield nt.assert_true, (a[0,...] == a[0]).all(), \
          'slicing with ellipsis failed'
    yield nt.assert_true, (a[0,...,0] == a[0,:,0]).all(), \
          'slicing with ellipsis failed'

def test_shifty_labels():
    arr = np.random.randn(2,5,6)
    a = DataArray( arr, 'xy' )
    # slicing out the "x" Axis triggered the unlabeled axis to change
    # name from "_2" to "_1".. make sure that this change is mapped
    b = a[0,:2]
    assert (b == arr[0,:2]).all(), 'shifty labels strike again!'

# -- Tests with "aix" slicing ------------------------------------------------
def test_axis_slicing():
    np_arr = np.random.randn(3,4,5)
    a = DataArray(np_arr, 'xyz')
    b = a[ a.aix.y[:2].x[::2] ]
    yield nt.assert_true, (b==a[::2,:2]).all(), 'unordered axis slicing failed'

    b = a[ a.aix.z[:2] ]
    yield nt.assert_true, (b==a.axis.z[:2]).all(), 'axis slicing inconsistent'
    yield nt.assert_true, b.labels == ('x', 'y', 'z')

def test_axis_slicing_both_ways():
    a = DataArray(np.random.randn(3,4,5), 'xyz')

    b1 = a.axis.y[::2].axis.x[1:]
    b2 = a[ a.aix.y[::2].x[1:] ]

    yield nt.assert_true, (b1==b2).all()
    yield nt.assert_true, b1.labels == b2.labels
    
# -- Testing utility functions -----------------------------------------------
from datarray.datarray import _expand_ellipsis, _make_singleton_axes

def test_ellipsis_expansion():
    slicing = ( slice(2), Ellipsis, 2 )
    fixed = _expand_ellipsis(slicing, 4)
    should_be = ( slice(2), slice(None), slice(None), 2 )
    yield nt.assert_true, fixed==should_be, 'wrong slicer1'
    fixed = _expand_ellipsis(slicing, 2)
    should_be = ( slice(2), 2 )
    yield nt.assert_true, fixed==should_be, 'wrong slicer2'

def test_singleton_axis_prep():
    b = DataArray( np.random.randn(5,6), 'xz' )
    slicing = ( None, )
    shape, axes, key = _make_singleton_axes(b, slicing)

    key_should_be = (slice(None), ) # should be trimmed
    shape_should_be = (1,5,6)
    ax_should_be = [ Axis(l, i, b) for i, l in enumerate((None, 'x', 'z')) ]

    yield nt.assert_true, key_should_be==key, 'key translated poorly'
    yield nt.assert_true, shape_should_be==shape, 'shape computed poorly'
    yield nt.assert_true, all([a1==a2 for a1,a2 in zip(ax_should_be, axes)]), \
          'axes computed poorly'

def test_singleton_axis_prep2():
    # a little more complicated
    b = DataArray( np.random.randn(5,6), 'xz' )
    slicing = ( 0, None )
    shape, axes, key = _make_singleton_axes(b, slicing)

    key_should_be = (0, ) # should be trimmed
    shape_should_be = (5,1,6)
    ax_should_be = [ Axis(l, i, b) for i, l in enumerate(('x', None, 'z')) ]

    yield nt.assert_true, key_should_be==key, 'key translated poorly'
    yield nt.assert_true, shape_should_be==shape, 'shape computed poorly'
    yield nt.assert_true, all([a1==a2 for a1,a2 in zip(ax_should_be, axes)]), \
          'axes computed poorly'
