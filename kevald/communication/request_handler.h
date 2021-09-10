#pragma once

#include "communication/communication_defs.h"
#include "routines/routine_finder.h"

namespace keval::communication {

/**
    Handles requests for the driver.
*/
class RequestHandler
{
public:
    void handle(RequestCallFunction& request);

    void handle(RequestReadBytes& request);

    void handle(RequestWriteBytes& request);

    void handle(RequestAllocate& request);

    void handle(RequestFree& request);

private:
    routines::RoutineFinder m_routineFinder;
};

}  // namespace keval::communication
