/** @tele-module **/

const { Component } = twl;

/**
 * This hook provides support for dynamic-refs.
 *
 * @returns {function} returns object whose keys are t-ref values of active refs.
 *   and values are refs.
 */
export function useRefs() {
    const component = Component.current;
    return function () {
        return component.__twl__.refs || {};
    };
}
